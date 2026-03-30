# Chapter 1: What Is System Design?

## What You Will Learn

- What system design actually means and why it is different from writing code
- The difference between an architect and a builder in software
- How to separate functional requirements from non-functional requirements
- Core concepts: latency, throughput, availability, consistency, and partition tolerance
- How to do quick back-of-envelope calculations
- A repeatable 4-step framework for tackling any system design problem

## Why This Chapter Matters

Imagine you are asked to build a house. You could start laying bricks right away. But without a blueprint, you might end up with a kitchen where the bathroom should be, walls that cannot support a second floor, and doors that open into walls.

System design is the blueprint for software. It is the process of deciding **how** the pieces of a system fit together before you start writing code. Whether you are preparing for a technical interview or building a real product, system design thinking separates engineers who build things that work from engineers who build things that work **at scale**.

Every major outage, every slow application, every system that crumbles under traffic -- these are usually not code bugs. They are design problems.

---

## 1.1 What Is System Design?

System design is the process of defining the architecture, components, modules, interfaces, and data flow of a system to satisfy specified requirements.

In simpler terms: it is deciding **what pieces you need** and **how they talk to each other**.

### The Architect vs The Builder

Think of constructing a skyscraper.

- The **architect** decides how many floors, where the elevators go, how the plumbing runs, and what materials can handle the load. They think about earthquakes, wind, and thousands of people using the building daily.
- The **builder** takes those plans and executes them. They pour concrete, wire electricity, and install fixtures.

In software:

- The **system designer** (architect) decides: Should we use one database or three? How do users authenticate? What happens when a server crashes? How do we handle 10 million requests per second?
- The **developer** (builder) writes the code that implements those decisions.

```
+--------------------------------------------------+
|              SYSTEM DESIGN PROCESS                |
+--------------------------------------------------+
|                                                   |
|   Requirements --> Architecture --> Components    |
|        |               |               |          |
|        v               v               v          |
|   "What does it    "How do the    "What does      |
|    need to do?"    pieces fit?"   each piece do?" |
|                                                   |
+--------------------------------------------------+
```

Most engineers start their careers as builders. System design is the skill that turns builders into architects.

### Real-World vs Interview System Design

System design shows up in two major places:

**In interviews:**
- You are given an open-ended problem: "Design Twitter" or "Design a URL shortener"
- You have 45-60 minutes to define requirements, sketch architecture, and discuss trade-offs
- The interviewer is evaluating your thinking process, not looking for one correct answer

**In the real world:**
- You are building a feature and need to decide how it fits into the existing system
- Your system is falling over under load and you need to figure out why
- You are starting a new project and need to choose the right database, message queue, and deployment strategy

The skills are the same. The difference is that in real life, you have more time and more information. In interviews, you have to make reasonable assumptions quickly.

---

## 1.2 Functional vs Non-Functional Requirements

Every system has two types of requirements. Confusing them is one of the most common mistakes in system design.

### Functional Requirements: What the System Does

These describe the **features** and **behaviors** of the system. They answer: "What can a user do?"

Examples for a social media app:
- Users can create an account
- Users can post text and images
- Users can follow other users
- Users see a feed of posts from people they follow
- Users can like and comment on posts

### Non-Functional Requirements: How the System Performs

These describe the **qualities** of the system. They answer: "How well does it work?"

Examples for the same social media app:
- The feed loads in under 200 milliseconds
- The system handles 50,000 concurrent users
- The system is available 99.99% of the time
- Data is never lost, even if a server crashes
- The system works for users in 30 countries

### The Iceberg Analogy

Functional requirements are the tip of the iceberg -- they are what users see. Non-functional requirements are the massive hidden part underneath -- they are what keeps the system from sinking.

```
          Functional Requirements
              (What users see)
         ___________________________
        /    Create account          \
       /     Post content             \
      /      Follow users              \
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  <-- Waterline
      \      99.99% uptime            /
       \     < 200ms latency          /
        \    50K concurrent users    /
         \   Data durability        /
          \  Global availability   /
           \  Security            /
            \  Compliance        /
             \__________________/
          Non-Functional Requirements
            (What keeps it running)
```

A system that has all the features but crashes every hour is useless. A system that is blazing fast but missing key features is also useless. You need both.

---

## 1.3 Core Concepts Defined Simply

These five concepts come up in every system design discussion. Let us define each one with a real-life analogy.

### Latency: How Long You Wait

**Definition:** The time it takes for a single request to travel from the client to the server and back.

**Analogy:** You walk into a coffee shop and order a latte. Latency is the time from when you say "one latte, please" to when the latte is in your hand.

**Common latency numbers every engineer should know:**

| Operation                          | Time          |
|------------------------------------|---------------|
| L1 cache reference                 | 0.5 ns        |
| L2 cache reference                 | 7 ns          |
| Main memory reference              | 100 ns        |
| SSD random read                    | 150 us        |
| HDD random read                   | 10 ms         |
| Send packet CA to Netherlands      | 150 ms        |
| Read 1 MB from memory              | 250 us        |
| Read 1 MB from SSD                 | 1 ms          |
| Read 1 MB from HDD                 | 20 ms         |
| Read 1 MB over 1 Gbps network      | 10 ms         |

**Key insight:** Latency is about **speed for one request**. Low latency means fast responses.

### Throughput: How Much Work Gets Done

**Definition:** The number of requests or operations a system can handle per unit of time.

**Analogy:** Back at the coffee shop. Throughput is the number of lattes the shop can make per hour. A shop might have low latency (each latte takes 2 minutes) but low throughput (only one barista, so 30 lattes per hour). Or it might have 5 baristas and make 150 lattes per hour.

**Key insight:** Throughput is about **volume**. High throughput means handling many requests.

**Latency vs Throughput:**

```
Latency (Speed)                Throughput (Volume)
+---------+                    +---------+
| Request |---> 50ms           | 1000    |
+---------+                    | req/sec |
                               +---------+
"How fast is one?"             "How many per second?"
```

You can have low latency but low throughput (a very fast single-lane road). You can have high throughput but high latency (a cargo ship carries a lot but takes weeks). The best systems optimize both.

### Availability: How Often It Works

**Definition:** The percentage of time a system is operational and accessible.

**Analogy:** A vending machine. If you walk up to it 100 times and it works 99 times, its availability is 99%.

**Availability is measured in "nines":**

| Availability | Downtime per year | Downtime per month | Downtime per day |
|-------------|-------------------|-------------------|-----------------|
| 99% (two nines) | 3.65 days | 7.3 hours | 14.4 minutes |
| 99.9% (three nines) | 8.77 hours | 43.8 minutes | 1.44 minutes |
| 99.99% (four nines) | 52.6 minutes | 4.38 minutes | 8.64 seconds |
| 99.999% (five nines) | 5.26 minutes | 26.3 seconds | 864 ms |

**Key insight:** Each additional "nine" is exponentially harder and more expensive to achieve. Going from 99.9% to 99.99% does not sound like much, but it means reducing downtime from 8.7 hours/year to 52 minutes/year.

### Consistency: Does Everyone See the Same Data?

**Definition:** Whether all users see the same data at the same time after a write operation.

**Analogy:** Imagine a shared Google Doc. If you type a sentence and your colleague immediately sees it, that is strong consistency. If there is a delay and they see the old version for a few seconds, that is eventual consistency.

**Types of consistency:**

- **Strong consistency:** After a write, all subsequent reads return the updated value. Everyone always sees the latest data.
- **Eventual consistency:** After a write, reads might return old data for a while, but eventually all copies will converge to the latest value.
- **Causal consistency:** If event A causes event B, everyone will see A before B. But unrelated events can appear in different orders.

### Partition Tolerance: What Happens When the Network Breaks?

**Definition:** The system continues to operate even when network communication between parts of the system fails.

**Analogy:** You have two offices in different cities connected by a phone line. Partition tolerance means work continues even if the phone line goes down. Each office keeps working independently and syncs up when the connection is restored.

### The CAP Theorem (Simplified)

The CAP theorem states that a distributed system can only guarantee **two out of three** properties:

- **C**onsistency: Every read gets the most recent write
- **A**vailability: Every request gets a response
- **P**artition tolerance: The system works despite network failures

```
              Consistency (C)
                   /\
                  /  \
                 /    \
                / CP   \
               /  systems\
              /    (e.g.,  \
             /   HBase,     \
            /    MongoDB*)    \
           /                   \
          /____________________\
         /\                   /\
        /  \      CA         /  \
       / AP \   systems     /    \
      / systems (traditional\    \
     / (Cassandra, RDBMS on  \   \
    /   DynamoDB) one node)   \  \
   /________________________________\
  Availability (A)    Partition Tolerance (P)

  * In practice, P is not optional in distributed
    systems. Networks WILL fail. So the real choice
    is between CP and AP.
```

**The practical takeaway:** Since network partitions are inevitable in distributed systems, you are really choosing between consistency and availability. Different parts of your system might make different choices.

---

## 1.4 Back-of-Envelope Estimation

System design problems often require you to estimate scale. You do not need exact numbers. You need reasonable approximations.

### Why Estimates Matter

If your system needs to handle 100 requests per second, a single server might work fine. If it needs to handle 1 million requests per second, you need a completely different architecture. Estimation helps you choose the right approach.

### Key Numbers to Remember

**Users and traffic:**
- 1 million seconds is about 12 days
- 1 billion seconds is about 31.7 years
- 1 day has about 86,400 seconds (round to 100,000 for estimation)
- 1 month has about 2.5 million seconds

**Data sizes:**
- 1 character (ASCII) = 1 byte
- 1 character (Unicode/UTF-8) = 1-4 bytes
- A typical tweet-length message = ~200 bytes
- A typical web page = ~2 MB
- A photo (compressed) = ~200 KB to 2 MB
- A short video = ~50 MB

**Storage:**
- 1 KB = 1,000 bytes (10^3)
- 1 MB = 1,000,000 bytes (10^6)
- 1 GB = 10^9 bytes
- 1 TB = 10^12 bytes
- 1 PB = 10^15 bytes

### Example: Estimating Storage for a Photo Sharing App

**Given:**
- 500 million users
- 10% are daily active users (50 million DAU)
- Each active user uploads 2 photos per day
- Average photo size: 500 KB

**Calculation:**

```
Photos per day    = 50M users x 2 photos = 100M photos/day
Storage per day   = 100M x 500 KB = 50 TB/day
Storage per year  = 50 TB x 365 = ~18 PB/year
```

That is a LOT of storage. This tells you immediately that you need distributed storage, a CDN for serving photos, and probably a strategy for compressing or tiering old photos.

### The Power of Round Numbers

Do not get caught up in exact math. Round aggressively:
- 365 days? Call it 400 (or 300 for conservative estimates)
- 86,400 seconds in a day? Call it 100,000
- 2.5 million seconds in a month? Call it 2 or 3 million

The goal is to land in the right order of magnitude, not the right decimal.

---

## 1.5 How to Approach a System Design Problem

Here is a repeatable 4-step framework that works for interviews and real-world design.

### Step 1: Clarify Requirements (5 minutes)

Do not start designing immediately. Ask questions first.

**Questions to ask:**
- Who are the users? How many?
- What are the core features? (Narrow down to 3-5)
- What are the scale requirements? (Users, requests per second, data volume)
- What are the non-functional requirements? (Latency, availability, consistency)
- Are there any constraints? (Budget, existing technology, regulatory)

**Example for "Design a URL Shortener":**
- How many URLs shortened per day? (100 million)
- How many redirects per day? (10 billion -- 100:1 read/write ratio)
- How long should shortened URLs be kept? (10 years by default)
- Should analytics be tracked? (Yes, click counts)
- URL format? (As short as possible, alphanumeric)

### Step 2: High-Level Design (10 minutes)

Sketch the major components and how they connect. Do not go deep yet.

```
+--------+      +---------------+      +-----------+
| Client | ---> | Load Balancer | ---> | Web Server|
+--------+      +---------------+      +-----------+
                                             |
                                             v
                                       +-----------+
                                       |  Database |
                                       +-----------+
```

Identify the main flows:
- How does a user shorten a URL?
- How does a user get redirected from a short URL?
- How are analytics collected?

### Step 3: Deep Dive (20 minutes)

Pick the most interesting or challenging components and design them in detail.

For the URL shortener, you might deep dive into:
- **URL generation:** How do you create short, unique IDs? (Base62 encoding, hash functions, pre-generated IDs)
- **Database schema:** What tables? What indexes?
- **Read optimization:** How do you serve 10 billion redirects per day quickly? (Caching, database read replicas)

### Step 4: Wrap Up (5 minutes)

Discuss:
- **Bottlenecks:** Where will the system fail under extreme load?
- **Trade-offs:** What did you sacrifice and why?
- **Future improvements:** What would you add with more time?
- **Monitoring:** How do you know the system is healthy?

### The Framework Visualized

```
+----------------------------------------------------------+
|          SYSTEM DESIGN FRAMEWORK (4 STEPS)                |
+----------------------------------------------------------+
|                                                           |
|  STEP 1: CLARIFY (5 min)                                 |
|  +-----------------------------------------------------+ |
|  | Users? Scale? Features? Constraints? Non-functional? | |
|  +-----------------------------------------------------+ |
|                          |                                |
|                          v                                |
|  STEP 2: HIGH-LEVEL DESIGN (10 min)                      |
|  +-----------------------------------------------------+ |
|  | Major components, APIs, data flow, basic diagram     | |
|  +-----------------------------------------------------+ |
|                          |                                |
|                          v                                |
|  STEP 3: DEEP DIVE (20 min)                              |
|  +-----------------------------------------------------+ |
|  | Pick 2-3 components. Detail schema, algorithms,      | |
|  | scaling strategies, failure handling                  | |
|  +-----------------------------------------------------+ |
|                          |                                |
|                          v                                |
|  STEP 4: WRAP UP (5 min)                                 |
|  +-----------------------------------------------------+ |
|  | Bottlenecks, trade-offs, monitoring, future work     | |
|  +-----------------------------------------------------+ |
|                                                           |
+----------------------------------------------------------+
```

---

## Trade-Offs Table

| Decision | Option A | Option B | When to Choose A | When to Choose B |
|----------|----------|----------|-----------------|-----------------|
| Consistency vs Availability | Strong consistency | Eventual consistency | Financial data, inventory | Social feeds, likes |
| Latency vs Throughput | Optimize for latency | Optimize for throughput | Real-time apps, gaming | Batch processing, analytics |
| Simplicity vs Scalability | Simple architecture | Complex distributed system | Early stage, < 1000 users | Millions of users, growth expected |
| Cost vs Performance | Budget-friendly | High performance | Startups, MVPs | Revenue-critical systems |
| Build vs Buy | Build custom | Use managed service | Unique requirements, competitive advantage | Standard problems (auth, payments) |

---

## Common Mistakes

1. **Jumping into design without clarifying requirements.** You cannot design a system if you do not know what it needs to do. Always ask questions first.

2. **Over-engineering from the start.** Not every system needs microservices, Kubernetes, and a distributed cache. Start simple and scale when needed.

3. **Ignoring non-functional requirements.** A system that has all the features but cannot handle 100 users is not a good design.

4. **Forgetting about failure.** Servers crash. Networks fail. Disks die. Your design must account for these realities.

5. **Not considering data volume.** "Store user data" sounds simple until you realize you have 500 million users each with 10 GB of data.

6. **Treating system design as memorization.** It is a thinking skill, not a trivia contest. Understanding trade-offs matters more than knowing specific technologies.

---

## Best Practices

1. **Always start with requirements.** Spend the first few minutes understanding what you are building and for whom.

2. **Design for the expected scale, not infinite scale.** If your system serves 1,000 users, a single database is fine. Do not add complexity you do not need yet.

3. **Think in terms of trade-offs, not best solutions.** Every decision has pros and cons. Acknowledge them.

4. **Use back-of-envelope math early.** Quick calculations prevent you from building a solution that is wildly under or over-provisioned.

5. **Draw diagrams.** A picture is worth a thousand words in system design. Visualize data flow and component interactions.

6. **Consider failure modes.** For each component, ask: "What happens if this fails?"

---

## Quick Summary

System design is the process of defining how the pieces of a software system fit together. It is the difference between an architect who plans the building and a builder who constructs it. Every system has functional requirements (what it does) and non-functional requirements (how well it does it). Five core concepts -- latency, throughput, availability, consistency, and partition tolerance -- form the vocabulary of system design. Back-of-envelope estimation helps you understand the scale of a problem. The 4-step framework (clarify, high-level design, deep dive, wrap up) gives you a repeatable approach to any system design challenge.

---

## Key Points

- System design is about deciding **how pieces fit together**, not writing code
- Functional requirements define features; non-functional requirements define quality
- Latency = speed of one request; throughput = volume of requests
- Availability is measured in "nines" -- each nine is exponentially harder
- The CAP theorem forces a choice between consistency and availability in distributed systems
- Back-of-envelope estimation helps you understand scale before you design
- The 4-step framework: Clarify, High-Level Design, Deep Dive, Wrap Up

---

## Practice Questions

1. You are designing a messaging app like WhatsApp. List 5 functional requirements and 5 non-functional requirements. How would you prioritize them?

2. A system has 99.95% availability. How many minutes of downtime does that allow per month? If the system has 3 independent components each with 99.95% availability, what is the overall system availability?

3. You are told a system handles 5,000 requests per second with an average latency of 20ms. The product team wants to add a feature that increases latency to 50ms per request. What is the impact on throughput, and what might you do about it?

4. Estimate the storage requirements for an email service with 1 billion users, where the average user sends 10 emails per day and the average email is 50 KB (including attachments). How much storage do you need per year?

5. For each of the following systems, would you prioritize consistency or availability, and why?
   - A banking transaction system
   - A social media news feed
   - An airline seat booking system
   - A content recommendation engine

---

## Exercises

**Exercise 1: Design Requirement Gathering**

Pick any application you use daily (Instagram, Spotify, Uber, etc.). Write down:
- 10 functional requirements
- 5 non-functional requirements
- Identify which non-functional requirements are most critical and explain why

**Exercise 2: Back-of-Envelope Practice**

Estimate the following:
- How many photos does Instagram store in total? (Hint: start with number of users, daily active users, photos per user per day, and how long Instagram has existed)
- How much bandwidth does YouTube need to serve video? (Hint: start with number of daily viewers, average video length, average video quality/bitrate)

Show your work step by step. Remember: the goal is the right order of magnitude.

**Exercise 3: Framework Practice**

Apply the 4-step framework to this problem: "Design a parking lot system." Spend 5 minutes on each step. Focus on:
- Clarifying questions you would ask
- High-level components
- One area to deep dive into
- Trade-offs you made

---

## What Is Next?

Now that you understand what system design is and have a framework for approaching problems, the next step is to learn about the most fundamental challenge: **scaling**. In Chapter 2, we will start with a single server and explore what happens as your system grows. You will learn the difference between vertical and horizontal scaling, understand stateless vs stateful architectures, and see how session handling works. These are the building blocks that every other concept in this book builds upon.
