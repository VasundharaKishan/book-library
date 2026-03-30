# Chapter 32: The System Design Interview Framework

You have spent dozens of hours learning about caching, databases, load balancers, message queues, and distributed systems. You can explain consistent hashing and the CAP theorem in your sleep. But when you sit down in a 45-minute system design interview and the interviewer says "Design WhatsApp," your mind goes blank. Where do you start? What do you say first? How do you know if you are going too deep or staying too shallow?

This chapter gives you a repeatable, four-step framework that works for every system design question. It is the same framework used by candidates who get offers at top tech companies, and it works because it mirrors how senior engineers actually approach problems in the real world: clarify the problem, sketch the big picture, dive into the hard parts, and reflect on trade-offs.

---

## What You Will Learn

- The four-step framework for system design interviews: Clarify, High-Level Design, Deep Dive, Wrap Up.
- Exactly what to say and do in each step, with time allocations.
- How to communicate effectively with your interviewer throughout.
- Red flags that hurt your chances and green flags that help.
- A complete sample 45-minute walkthrough.
- What interviewers are actually evaluating.

---

## Why This Chapter Matters

Technical knowledge without a delivery framework is like having all the ingredients but no recipe. The framework is what transforms your knowledge into a coherent, impressive interview performance. Without it, even brilliant engineers ramble, skip critical steps, or spend 30 minutes on a detail that does not matter.

The framework also reduces anxiety. When you know exactly what to do in each phase, you do not waste mental energy wondering "what should I talk about next?" You can focus entirely on the actual design.

---

## 32.1 The Four Steps at a Glance

```
+----------------------------------------------------------+
|               45-Minute Interview Timeline                |
+----------------------------------------------------------+
|                                                          |
|  Step 1: CLARIFY (5-7 min)                               |
|  [=======]                                               |
|  Ask questions. Define scope. Estimate scale.            |
|                                                          |
|  Step 2: HIGH-LEVEL DESIGN (15-20 min)                   |
|  [=====================]                                 |
|  Draw the architecture. Define APIs. Data model.         |
|                                                          |
|  Step 3: DEEP DIVE (15-20 min)                           |
|  [=====================]                                 |
|  Go deep on 2-3 critical components.                     |
|                                                          |
|  Step 4: WRAP UP (3-5 min)                               |
|  [=====]                                                 |
|  Summarize. Discuss trade-offs. Identify improvements.   |
|                                                          |
+----------------------------------------------------------+
```

Each step has a clear purpose, a set of activities, and a time budget. Let us explore each one in detail.

---

## 32.2 Step 1: Clarify the Requirements (5-7 minutes)

This is the most underrated step. Many candidates skip it entirely and jump straight to drawing boxes. That is a mistake. Clarifying requirements shows the interviewer that you think before you build -- a hallmark of senior engineers.

### What to Do

1. **Restate the problem** in your own words to confirm understanding.
2. **Ask clarifying questions** about functional requirements.
3. **Ask about non-functional requirements** (scale, latency, availability).
4. **Identify what is in scope and out of scope.**
5. **Do back-of-the-envelope estimation** (from Chapter 31).

### Questions to Ask

Here is a checklist of questions organized by category. You will not ask all of them -- pick the ones most relevant to the problem.

**Functional scope:**
- What are the core features we need to support?
- Who are the users? (consumers, businesses, internal?)
- What platforms? (mobile, web, API?)
- Do we need real-time functionality?

**Scale and traffic:**
- How many DAU should we design for?
- What is the expected read/write ratio?
- How much data are we storing?
- Are there any spiky traffic patterns?

**Non-functional requirements:**
- What is the latency target? (p50, p99)
- What availability do we need? (99.9%? 99.99%?)
- Is consistency or availability more important?
- Do we need to support multiple regions?

**Constraints:**
- Are there any specific technology constraints?
- Do we need backward compatibility with existing systems?
- What is the budget? (for cost-sensitive designs)

### Example: Clarifying "Design a Chat System"

```
Candidate: "To make sure I understand, we are designing a real-time
            messaging system similar to WhatsApp or Slack. Let me
            ask a few questions to narrow the scope."

Candidate: "Is this 1:1 chat, group chat, or both?"
Interviewer: "Both. Start with 1:1 and we can extend to groups."

Candidate: "What about media -- just text, or also images/files?"
Interviewer: "Text for now. Mention how you would add media."

Candidate: "How many DAU are we targeting?"
Interviewer: "50 million."

Candidate: "What about message delivery guarantees? At-most-once,
            at-least-once, or exactly-once?"
Interviewer: "At-least-once with deduplication on the client."

Candidate: "Do we need message history / persistence?"
Interviewer: "Yes, users should see their message history."

Candidate: "Any latency requirements?"
Interviewer: "Messages should be delivered in under 500ms."
```

After this exchange, the candidate and interviewer have a shared understanding of what to build.

### Back-of-the-Envelope Estimation

After clarifying requirements, spend 2-3 minutes on quick estimates:

```
Candidate: "Let me do some quick math.

  50M DAU x 40 messages sent per day = 2 billion messages/day
  QPS = 2B / 86,400 = ~23,000 messages/second
  Peak QPS = ~70,000 messages/second

  Storage per message: ~200 bytes (text + metadata)
  Daily storage: 2B x 200 bytes = 400 GB/day
  Yearly: ~146 TB

  This is a write-heavy system with real-time delivery needs.
  We will need WebSockets and a pub/sub mechanism."
```

### Common Mistake: Going Too Deep Too Early

Do NOT start designing the database schema or debating Redis vs Memcached in this step. You are setting the stage, not building the house.

---

## 32.3 Step 2: High-Level Design (15-20 minutes)

This is the main act. You will draw the architecture, define APIs, and outline the data model.

### What to Do

1. **Draw the architecture diagram** on the whiteboard (or shared doc).
2. **Define the API** for core operations.
3. **Outline the data model** (key tables/collections and their relationships).
4. **Walk through the main user flows** end-to-end.
5. **Check in with the interviewer** to see if they want to go deeper on anything.

### Drawing the Architecture

Start with the user on the left and the data store on the right. Add components as needed:

```
+---------+       +-----------+       +------------+       +----------+
| Client  |------>|  Load     |------>|  App       |------>| Database |
| (Mobile |       |  Balancer |       |  Server(s) |       |          |
|  / Web) |       +-----------+       +------------+       +----------+
+---------+                                  |
                                             v
                                       +----------+
                                       |  Cache   |
                                       +----------+
```

Then add detail as you talk through the design:

```
+---------+     +--------+     +------------+     +-----------+
| Client  |<--->|  API   |<--->|  Chat      |<--->| Message   |
| (WS)    |     | Gateway|     |  Service   |     | Store     |
+---------+     +--------+     +------------+     | (Cassandra|
                                     |            +-----------+
                                     v
                               +------------+     +-----------+
                               | Presence   |<--->| Redis     |
                               | Service    |     | (online   |
                               +------------+     |  status)  |
                                                  +-----------+
                               +------------+     +-----------+
                               | Push       |<--->| APNs/FCM  |
                               | Service    |     | (offline  |
                               +------------+     |  push)    |
                                                  +-----------+
```

### Defining the API

Keep APIs simple. Use REST-style or describe the operations:

```
POST /api/messages
  Body: { sender_id, receiver_id, content, timestamp }
  Response: { message_id, status }

GET /api/messages?user_id=X&contact_id=Y&before=timestamp&limit=50
  Response: { messages: [...], has_more: true/false }

WebSocket: /ws/chat
  Connect: { user_id, auth_token }
  Send: { type: "message", receiver_id, content }
  Receive: { type: "message", sender_id, content, timestamp }
```

### Outlining the Data Model

```
Messages Table:
+-------------+-----------+----------------------------------+
| Column      | Type      | Notes                            |
+-------------+-----------+----------------------------------+
| message_id  | UUID      | Primary key (time-based UUID)    |
| sender_id   | BIGINT    | Who sent it                      |
| receiver_id | BIGINT    | Who receives it                  |
| content     | TEXT      | Message text                     |
| created_at  | TIMESTAMP | When it was sent                 |
| status      | ENUM      | sent / delivered / read          |
+-------------+-----------+----------------------------------+

Partition key: (sender_id, receiver_id) for conversation-based queries
```

### Walking Through User Flows

Pick the 2-3 most important user flows and trace them through your architecture:

```
Flow: User A sends a message to User B

1. User A's client sends message via WebSocket to API Gateway
2. API Gateway routes to Chat Service
3. Chat Service stores message in Message Store
4. Chat Service checks if User B is online (Presence Service)
5. If online: deliver via WebSocket connection to User B
6. If offline: send push notification via Push Service
7. User B's client acknowledges receipt
8. Chat Service updates message status to "delivered"
```

### Check In With the Interviewer

After completing the high-level design (about 15-20 minutes in), pause and ask:

```
"This is the high-level architecture. Before I go deeper,
is there a particular component you would like me to dive into?
I was thinking of exploring [X] and [Y] in more detail."
```

This shows collaboration and lets the interviewer steer toward what they care about.

---

## 32.4 Step 3: Deep Dive (15-20 minutes)

This is where you demonstrate depth. Pick 2-3 components and go deep on design decisions, trade-offs, and edge cases.

### What to Do

1. **Pick 2-3 areas** to dive deep (or follow the interviewer's guidance).
2. **Discuss design choices and trade-offs** for each area.
3. **Handle edge cases** and failure scenarios.
4. **Optimize** for the non-functional requirements identified in Step 1.

### What to Dive Into

Choose areas that are:
- **Critical to the system** -- If this component fails, the whole system breaks.
- **Technically interesting** -- Shows depth of knowledge.
- **Relevant to the requirements** -- Addresses the specific scale/latency/consistency needs.

Common deep-dive topics:

| Topic | What to Discuss |
|-------|-----------------|
| Database choice | SQL vs NoSQL, partition strategy, replication |
| Caching strategy | What to cache, eviction policy, consistency |
| Scaling bottlenecks | What breaks first, how to scale horizontally |
| Data consistency | Strong vs eventual, conflict resolution |
| Failure handling | What happens when X goes down? |
| Real-time delivery | WebSockets, long polling, SSE |
| Rate limiting | How to protect the system from abuse |
| Monitoring | Key metrics, alerting, debugging |

### Example Deep Dive: Message Delivery Guarantee

```
Candidate: "Let me dive into how we guarantee message delivery.

The challenge is that the recipient might be offline, or the
network might drop the WebSocket connection mid-delivery.

Here is our delivery flow:

1. Sender sends message. Server stores it in the database
   BEFORE attempting delivery. This guarantees durability.

2. Server assigns a monotonically increasing sequence number
   per conversation. This lets the client detect gaps.

3. If recipient is online, push via WebSocket. The recipient
   client sends an ACK back. Server updates status to
   'delivered.'

4. If no ACK within 5 seconds, retry 3 times with
   exponential backoff.

5. If recipient is offline, queue the message. When the
   recipient reconnects, they pull all undelivered messages
   using the last sequence number they received.

6. The client deduplicates using message_id to handle
   at-least-once delivery.

Edge case: What if the server crashes after storing the
message but before delivering it? On restart, the server
scans for messages in 'sent' status older than 30 seconds
and retries delivery.

Edge case: What if both clients are on different servers?
We use a pub/sub system (Redis Pub/Sub or Kafka) so that
the server holding User B's WebSocket receives the message
from the server that accepted User A's request."
```

This kind of deep dive shows the interviewer that you think about failure modes, edge cases, and real-world reliability.

---

## 32.5 Step 4: Wrap Up (3-5 minutes)

The wrap-up is your chance to show big-picture thinking and self-awareness.

### What to Do

1. **Summarize** the design in 2-3 sentences.
2. **Discuss trade-offs** you made and why.
3. **Identify improvements** you would make with more time.
4. **Mention operational concerns** (monitoring, deployment, testing).

### Example Wrap Up

```
Candidate: "To summarize, we designed a real-time chat system
that handles 50M DAU with WebSocket-based delivery, Cassandra
for message storage, Redis for presence and pub/sub, and a
push notification service for offline users.

Key trade-offs:
- We chose eventual consistency for message delivery status
  to favor availability and speed over strict ordering.
- We used Cassandra over PostgreSQL because our access pattern
  is append-heavy and partition-friendly.

If I had more time, I would explore:
- End-to-end encryption and key management
- Group chat fan-out optimization
- Media message support with CDN integration
- Message search using Elasticsearch
- Rate limiting and spam detection

For monitoring, I would track: message delivery latency (p50,
p99), WebSocket connection count, undelivered message queue
depth, and database write latency."
```

---

## 32.6 Communication Tips

How you communicate is as important as what you design. Here are the behaviors that set top candidates apart.

### Think Out Loud

The interviewer cannot read your mind. Narrate your thought process:

```
GOOD: "I am choosing Cassandra here because our write volume
      is very high and our access pattern is partition-friendly.
      We always query messages by conversation, which maps
      perfectly to Cassandra's partition key."

BAD:  *draws Cassandra on the whiteboard without explanation*
```

### Collaborate, Do Not Lecture

Treat the interview as a working session with a colleague, not a presentation:

```
GOOD: "I am thinking of using a message queue here to decouple
      the write path from the delivery path. Does that align
      with what you are thinking, or would you like me to
      explore a different approach?"

BAD:  *talks for 20 minutes straight without pause*
```

### Manage Your Time

Keep a mental clock. If you are 25 minutes in and still on the high-level design, you need to move to the deep dive.

```
+--------+--------+-----------+--------+
| 0-7min | 7-25min| 25-42min  | 42-45  |
| Clarify| Design | Deep Dive | Wrap   |
+--------+--------+-----------+--------+
```

### Use the Whiteboard Effectively

- Draw big. Small diagrams are hard to read and modify.
- Use consistent notation. Boxes for services, cylinders for databases, arrows for data flow.
- Label everything. Do not make the interviewer guess what a box represents.
- Leave space. You will need to add components as you go deeper.

---

## 32.7 Red Flags and Green Flags

### Red Flags (Things That Hurt You)

| Red Flag | Why It Hurts |
|----------|-------------|
| Jumping to solution without asking questions | Shows lack of engineering rigor |
| Only one approach considered | Unable to reason about trade-offs |
| Over-engineering simple problems | Using Kafka for 100 QPS |
| Under-engineering complex problems | Single database for 1M QPS |
| Ignoring non-functional requirements | Not discussing scalability or availability |
| Cannot handle pushback | Gets defensive when interviewer challenges a decision |
| Silent thinking for long periods | Interviewer cannot evaluate your thought process |
| Ignoring the interviewer's hints | Missing guidance toward what they want to discuss |
| Memorized solution delivery | Reciting a textbook answer without understanding trade-offs |
| No estimation or numbers | Cannot reason about scale |

### Green Flags (Things That Help You)

| Green Flag | Why It Helps |
|------------|-------------|
| Asks thoughtful clarifying questions | Shows product sense and engineering maturity |
| Estimates scale before designing | Demonstrates quantitative thinking |
| Explains trade-offs for each decision | Shows depth and experience |
| Handles edge cases proactively | Thinks about what can go wrong |
| Adapts when interviewer steers | Collaborative and flexible |
| Discusses monitoring and operations | Thinks beyond just building the system |
| Draws clean, organized diagrams | Communicates complex ideas clearly |
| Self-corrects and iterates | Shows intellectual honesty |
| Considers cost implications | Practical engineering judgment |
| Mentions security and privacy | Awareness of real-world concerns |

---

## 32.8 Sample 45-Minute Walkthrough: "Design a News Feed"

Here is how a strong candidate would spend their 45 minutes on "Design a News Feed" (like Facebook or Twitter).

### Minutes 0-6: Clarify

```
Candidate: "I want to make sure I understand the scope. We are
designing the home feed -- the page where users see posts from
people they follow, sorted by relevance or time. Is that right?"

Interviewer: "Yes."

Candidate: "A few questions:
- What types of content? Text, images, videos?
- Do we need a ranking algorithm, or is reverse chronological OK?
- How many DAU?
- Is this global or single-region?"

Interviewer: "Text and images. Ranked feed. 200M DAU. Global."

Candidate: "OK, let me estimate scale quickly.
- 200M DAU, each views feed ~10 times/day = 2B feed loads/day
- Feed load QPS = 2B / 86,400 = ~23,000 QPS
- Peak = ~70,000 QPS
- Each feed shows 20 posts = 1.4 billion post reads/day
  (but cached, so actual DB reads are much lower)
- Writes: ~50M posts/day = ~580 posts/second
- This is extremely read-heavy. Caching is critical."
```

### Minutes 6-22: High-Level Design

```
Candidate draws:

+--------+    +----------+    +----------+    +---------+
| Client |--->| API      |--->| Feed     |--->| Post    |
|        |    | Gateway  |    | Service  |    | Storage |
+--------+    +----------+    +----------+    +---------+
                                   |
                                   v
                              +----------+    +---------+
                              | Feed     |--->| Feed    |
                              | Cache    |    | Cache   |
                              | Builder  |    | (Redis) |
                              +----------+    +---------+
                                   |
                                   v
                              +----------+    +---------+
                              | Social   |--->| Graph   |
                              | Graph    |    | DB      |
                              | Service  |    |         |
                              +----------+    +---------+

"When a user requests their feed, the Feed Service checks
the Feed Cache first. If it is a cache hit, we return the
pre-computed feed. If it is a miss, the Feed Builder
constructs the feed by:

1. Querying the Social Graph for the user's following list
2. Fetching recent posts from each followed user
3. Ranking the posts
4. Caching the result
5. Returning the top 20 posts

For writes: when a user creates a post, we store it and
then fan out to followers' cached feeds.

API:
  GET /feed?user_id=X&cursor=abc&limit=20
  POST /posts { user_id, content, media_ids }

Data model:
  Posts: { post_id, author_id, content, media_urls,
           created_at, like_count }
  Follow: { follower_id, followee_id, created_at }
  Feed Cache: per-user sorted list of post_ids in Redis"
```

Candidate walks through the create-post and view-feed flows.

### Minutes 22-40: Deep Dive

```
Candidate: "I would like to dive into two areas:
1. Fan-out strategy (push vs pull)
2. Feed ranking

DEEP DIVE 1: Fan-out

The key decision is push (fan-out on write) vs pull
(fan-out on read).

Push model:
  When User A posts, write the post_id to the feed cache
  of every follower. If A has 1,000 followers, that is
  1,000 cache writes.

  Pros: Feed reads are instant (pre-computed).
  Cons: Celebrity problem. If a user has 10M followers,
        one post triggers 10M writes.

Pull model:
  When User B requests their feed, query all followees'
  recent posts, merge, rank, return.

  Pros: No celebrity problem. No write amplification.
  Cons: Slow feed reads. Must query N users' posts.

Hybrid approach (what Facebook and Twitter actually do):
  - For normal users (< 10K followers): push model
  - For celebrities (> 10K followers): pull model
  - When building a feed, merge the cached feed (push)
    with live queries for celebrity posts (pull)

This gives us fast reads for most content while avoiding
the celebrity write amplification problem.

DEEP DIVE 2: Feed ranking

Instead of reverse chronological, we rank by relevance.
Features used for ranking:

  - Recency (newer posts score higher)
  - Engagement (likes, comments, shares)
  - Relationship strength (how often user interacts
    with the author)
  - Content type preference (does user engage more
    with images or text?)

The ranking model runs at feed-build time. We can use a
lightweight ML model (logistic regression or small neural
net) that scores each candidate post and returns the
top 20.

For latency: pre-compute features offline, store in a
feature store, and do only the scoring online. Target:
<100ms for ranking 500 candidate posts."
```

### Minutes 40-45: Wrap Up

```
Candidate: "To summarize:
- Feed system for 200M DAU, 23K QPS average, 70K peak
- Hybrid fan-out: push for regular users, pull for celebrities
- Redis-based feed cache for sub-10ms feed reads
- ML-based ranking for relevance

Trade-offs:
- Hybrid complexity vs pure push/pull simplicity
- Eventual consistency in feed (acceptable for social media)
- Cache memory cost vs read latency

With more time, I would explore:
- Content moderation pipeline before feed insertion
- A/B testing framework for ranking models
- Multi-region feed consistency
- Ads insertion into the feed
- Rate limiting on post creation to prevent spam

For monitoring: feed build latency, cache hit rate,
fan-out queue depth, ranking model latency, and
feed freshness (time between post creation and feed
appearance)."
```

---

## 32.9 What Interviewers Are Actually Looking For

Different companies weight these differently, but here are the core evaluation criteria:

### Technical Competence

- Can you design a system that actually works at the stated scale?
- Do you understand the fundamental building blocks (databases, caches, queues, load balancers)?
- Can you make appropriate technology choices and justify them?

### Problem-Solving Approach

- Do you break down the problem systematically?
- Can you identify the hard parts of the problem?
- Do you consider multiple approaches before committing?

### Trade-off Analysis

- Can you articulate the pros and cons of your design decisions?
- Do you understand that every choice has a cost?
- Can you adapt your design when constraints change?

### Communication

- Can you explain complex ideas clearly?
- Do you organize your thoughts logically?
- Do you collaborate with the interviewer?

### Scope Management

- Can you identify what is in scope and out of scope?
- Do you prioritize the most important features?
- Can you manage your time effectively during the interview?

### Seniority Signals

| Level | What Interviewers Look For |
|-------|--------------------------|
| Junior | Understands basic components. Can draw a reasonable architecture. |
| Mid | Makes good technology choices. Handles common edge cases. |
| Senior | Deep trade-off analysis. Discusses operational concerns. Drives the conversation. |
| Staff+ | Considers organizational impact. Discusses multi-year evolution. Addresses cost and business trade-offs. |

---

## Common Mistakes

1. **Skipping Step 1.** Jumping to the solution without understanding the problem. You might design the wrong system entirely.

2. **Spending too long on estimation.** Estimation should take 2-3 minutes, not 15. It supports the design, it is not the design.

3. **Drawing before thinking.** Taking 30 seconds to mentally outline before you start drawing leads to a much cleaner diagram.

4. **Going too deep too early.** Discussing database indexing strategies before you have a high-level architecture wastes precious time.

5. **Ignoring the interviewer's hints.** If the interviewer says "interesting, how would you handle the case where..." -- that is where they want you to go. Follow their lead.

6. **One-size-fits-all answers.** Using the exact same architecture for a 100-user internal tool and a 100-million-user consumer app shows lack of judgment.

7. **No wrap-up.** Ending abruptly without summarizing makes it feel incomplete.

---

## Best Practices

1. **Practice with a timer.** Run mock interviews with a 45-minute clock. Time management is a skill that requires practice.

2. **Use a consistent notation.** Develop your own visual language: boxes for services, cylinders for databases, arrows for data flow, clouds for external services.

3. **Prepare "deep dive" topics.** For each system you study, prepare 2-3 topics you can dive deep on. Database choice, caching strategy, and failure handling are almost always relevant.

4. **Study real systems.** Read engineering blogs from Netflix, Uber, Twitter, and Facebook. Understanding how real systems work gives you authentic material.

5. **Practice explaining trade-offs.** For every design decision, be ready to say: "I chose X over Y because Z. The downside of X is W, but in our case that is acceptable because..."

6. **Record yourself.** Watch your practice sessions. Are you clear? Do you ramble? Do you use the whiteboard effectively?

---

## Quick Summary

The four-step framework structures your system design interview into Clarify (5-7 min), High-Level Design (15-20 min), Deep Dive (15-20 min), and Wrap Up (3-5 min). In Step 1, ask clarifying questions and estimate scale. In Step 2, draw the architecture, define APIs, and outline the data model. In Step 3, go deep on 2-3 critical components with trade-off analysis. In Step 4, summarize, discuss trade-offs, and mention improvements. Throughout, think out loud, collaborate with the interviewer, and manage your time.

---

## Key Points

- Never jump to the solution. Always start by clarifying requirements and estimating scale.
- The high-level design should include an architecture diagram, API definitions, and a data model.
- Deep dives should focus on 2-3 areas that are critical, technically interesting, and relevant to the requirements.
- Always discuss trade-offs. Every design decision has pros and cons.
- Communicate like a colleague, not a lecturer. Check in with the interviewer regularly.
- Green flags: thoughtful questions, quantitative thinking, trade-off analysis, edge case handling.
- Red flags: no clarification, silent thinking, ignoring hints, memorized answers.
- The wrap-up is your chance to show big-picture thinking and self-awareness.

---

## Practice Questions

1. You are 20 minutes into a 45-minute interview and you are still defining APIs for your high-level design. What should you do?

2. The interviewer asks you to "Design Uber." Write down the 5 most important clarifying questions you would ask before starting the design.

3. You chose PostgreSQL for your database, and the interviewer pushes back: "At 500,000 writes per second, will PostgreSQL handle this?" How do you respond? (Hint: this is not about defending your choice -- it is about demonstrating trade-off thinking.)

4. What is the difference between how a junior engineer and a senior engineer would wrap up a system design interview?

5. An interviewer gives you the hint: "Think about what happens when one of your services goes down." What are they actually asking you to discuss?

---

## Exercises

**Exercise 1: Timed Mock Interview**

Set a 45-minute timer and design "an online file storage system like Google Drive" using the four-step framework. Record the time you spend on each step. After the timer, evaluate: did you cover all four steps? Did you go too deep on any one area? Did you discuss trade-offs?

**Exercise 2: Trade-off Practice**

For each of these design decisions, write 2 pros and 2 cons:
- Using a NoSQL database (like DynamoDB) vs a relational database (like PostgreSQL) for a social media post store.
- Fan-out on write vs fan-out on read for a news feed.
- WebSockets vs long polling for real-time notifications.
- Monolithic architecture vs microservices for a startup's MVP.
- Strong consistency vs eventual consistency for a messaging app.

**Exercise 3: Interviewer Perspective**

You are the interviewer evaluating a candidate designing a URL shortener. Write a scoring rubric with 5 criteria, each scored 1-5. What would a score of 1 look like vs a score of 5 for each criterion? Use this rubric to evaluate your own practice interviews.

---

## What Is Next?

You now have the framework to deliver a structured, impressive system design interview. In the next chapter, we will catalog the most common design patterns that appear across system design problems -- reusable solutions like Circuit Breaker, CQRS, Saga, and Sidecar that you can pull out of your toolkit whenever they fit.
