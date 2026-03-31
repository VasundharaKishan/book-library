# Chapter 29: Code Review Culture

## What You Will Learn

- Why code reviews matter more than most teams realize
- What to look for in a code review (and what NOT to focus on)
- How to give constructive feedback that improves code AND relationships
- How to receive feedback without taking it personally
- Optimal pull request size and how to keep PRs small
- A practical code review checklist
- How to use automated checks to free reviewers for higher-level thinking

## Why This Chapter Matters

Code review is not about catching bugs. Well, it catches some bugs. But its real value runs much deeper.

Code review is how a team maintains quality standards. It is how junior developers learn from seniors, and how seniors discover blind spots they did not know they had. It is how knowledge spreads across the team so that no one person is the only one who understands a critical system. It is how your codebase stays consistent instead of becoming a patchwork of different styles and approaches.

Teams without code review gradually accumulate inconsistencies, shortcuts, and knowledge silos. One developer writes beautiful code. Another writes spaghetti. Nobody notices until the spaghetti developer goes on vacation and nobody can maintain their code.

Code review is the team's immune system. This chapter teaches you how to make it effective, constructive, and sustainable.

---

## Why Code Reviews Matter

```
THE BENEFITS OF CODE REVIEW:

  +-----------------------------------------------------+
  |                                                     |
  |  1. KNOWLEDGE SHARING                               |
  |     Every review teaches something. The author       |
  |     learns from feedback. The reviewer learns        |
  |     from reading the code.                           |
  |                                                     |
  |  2. CONSISTENCY                                     |
  |     Reviews enforce shared standards. The codebase   |
  |     reads like it was written by one team, not       |
  |     twelve individuals.                              |
  |                                                     |
  |  3. BUG PREVENTION                                  |
  |     A second pair of eyes catches logic errors,      |
  |     edge cases, and security issues that tests miss. |
  |                                                     |
  |  4. DESIGN IMPROVEMENT                              |
  |     Reviewers spot over-engineering, missed           |
  |     abstractions, and simpler alternatives.          |
  |                                                     |
  |  5. TEAM OWNERSHIP                                  |
  |     When everyone reviews each other's code,         |
  |     the entire team owns the entire codebase.        |
  |     No knowledge silos.                              |
  |                                                     |
  +-----------------------------------------------------+
```

### The Cost of Skipping Reviews

```
WITHOUT CODE REVIEW:

  Developer A                Developer B
  +------------------+      +------------------+
  | Uses camelCase   |      | Uses snake_case  |
  | Handles errors   |      | Ignores errors   |
  | Writes tests     |      | Skips tests      |
  | Small methods    |      | 200-line methods |
  +------------------+      +------------------+

  6 months later:
  +------------------------------------------+
  | Codebase is a mess                       |
  | - Mixed naming conventions               |
  | - Some parts tested, some not            |
  | - Nobody can maintain Developer B's code |
  | - New hires are confused by the chaos    |
  +------------------------------------------+

WITH CODE REVIEW:

  Developer A reviews B    Developer B reviews A
  +------------------+      +------------------+
  | "Use camelCase   |      | "This abstraction|
  |  like the rest   |      |  is clever --    |
  |  of the project" |      |  let me learn    |
  |                  |      |  this approach"  |
  | "Add error       |      |                  |
  |  handling here"  |      | "Why not use the |
  |                  |      |  factory pattern |
  | "This needs a    |      |  here?"          |
  |  test"           |      |                  |
  +------------------+      +------------------+

  6 months later:
  +------------------------------------------+
  | Codebase is consistent                   |
  | - Unified conventions                    |
  | - Comprehensive test coverage            |
  | - Both developers can maintain all code  |
  | - New hires onboard quickly              |
  +------------------------------------------+
```

---

## What to Look for in a Code Review

Not all review comments are equally valuable. Focus on the things that matter most:

```
REVIEW PRIORITY PYRAMID:

                    /\
                   /  \
                  / BUG \
                 / LOGIC \        <-- HIGHEST PRIORITY
                / SECURITY \       Correctness and safety
               /   ISSUES   \
              +--------------+
              |   DESIGN     |    <-- HIGH PRIORITY
              |  Structure,  |     Architecture, patterns
              |  abstractions|
              +--------------+
              | MAINTAINAB.  |    <-- MEDIUM PRIORITY
              | Readability, |     Names, complexity
              | clarity      |
              +--------------+
              |    STYLE     |    <-- LOW PRIORITY
              | Formatting,  |     Automate this!
              | whitespace   |
              +--------------+

  Spend most of your review energy at the TOP of the pyramid.
  Automate the BOTTOM with linters and formatters.
```

### High-Priority Review Items

#### 1. Correctness

Does the code actually do what it is supposed to do? Check edge cases and boundary conditions.

```java
// REVIEW CATCH: Off-by-one error
// The developer wrote:
for (int i = 0; i <= items.size(); i++) {  // Bug: <= should be <
    process(items.get(i));  // ArrayIndexOutOfBoundsException!
}

// Review comment:
// "This loop will throw on the last iteration. Use i < items.size()"
```

#### 2. Error Handling

What happens when things go wrong? Are errors handled, or silently swallowed?

```python
# REVIEW CATCH: Swallowed exception
try:
    result = external_api.call(data)
except Exception:
    pass  # Silently swallowed! Bug reports will be impossible.

# Review comment:
# "This catches and ignores all exceptions. At minimum, log the
# error. Better: handle specific exceptions and re-raise unexpected ones."
```

#### 3. Security

Is user input validated? Are there SQL injection or XSS vulnerabilities?

```java
// REVIEW CATCH: SQL injection
String query = "SELECT * FROM users WHERE name = '" + userName + "'";
// If userName is "'; DROP TABLE users; --", disaster.

// Review comment:
// "Use parameterized queries to prevent SQL injection:
// PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name = ?");
// ps.setString(1, userName);"
```

#### 4. Design

Is the solution well-structured? Is it too complex? Too clever?

```python
# REVIEW CATCH: Over-engineering
class AbstractStrategyFactoryProvider:
    def create_strategy_factory(self, context):
        return StrategyFactory(context.get_provider())

# Review comment:
# "This adds two layers of indirection for a feature that
# has exactly one implementation. Can we simplify to a direct
# function call? We can add abstraction when we need it."
```

### Low-Priority Items (Automate These)

- **Formatting:** Spaces, tabs, line length. Use a formatter (Prettier, Black, google-java-format).
- **Import order:** Use an import sorter.
- **Naming conventions:** Use a linter rule.
- **Unused variables:** Use a linter.

```
AUTOMATE THE STYLE ARGUMENTS:

  +-----------+                   +-----------+
  | Developer | "You used tabs!" | Developer |
  |     A     |<---------------->|     B     |
  +-----------+ "Spaces are      +-----------+
                 better!"

  This argument has been going on since 1970.
  End it with a formatter.

  +-----------+     +----------+     +-----------+
  | Developer |---->| Prettier |---->| Formatted |
  |     A     |     | / Black  |     | Code      |
  +-----------+     +----------+     +-----------+

  Nobody argues with the formatter. Problem solved.
```

---

## Giving Feedback: The Art of Constructive Review

How you say something matters as much as what you say. A review comment can teach and inspire, or it can demoralize and antagonize.

### Principles for Giving Feedback

#### 1. Comment on the Code, Not the Person

```
BAD:  "You clearly don't understand how exceptions work."
GOOD: "This catch block swallows the exception. Consider logging
       it or re-throwing it so we can diagnose failures."

BAD:  "This is wrong."
GOOD: "This will throw a NullPointerException if the user has no
       email set. Could we add a null check here?"

BAD:  "Why would you do it this way?"
GOOD: "I think using a Map here instead of a switch would make
       it easier to add new cases. What do you think?"
```

#### 2. Explain the WHY, Not Just the WHAT

```
BAD:  "Use final here."
GOOD: "Making this field final ensures it cannot be reassigned
       after construction, which prevents a category of bugs
       where the dependency is accidentally replaced."

BAD:  "Extract a method."
GOOD: "This block of 30 lines handles validation, and the rest
       of the method handles processing. Extracting validate()
       would make the flow clearer and let us test validation
       independently."
```

#### 3. Ask Questions Instead of Making Demands

```
DEMANDING: "Change this to use a stream."
ASKING:    "Have you considered using a stream here?
            It might make the filtering more readable."

DEMANDING: "This needs to be refactored."
ASKING:    "Do you think this method is doing too much?
            I count three distinct responsibilities."
```

#### 4. Distinguish Between Blocking and Non-Blocking Comments

```
BLOCKING (must fix before merge):
"Bug: This will cause a NullPointerException when user.getEmail()
 returns null, which happens for unverified accounts."

NON-BLOCKING (nice to have, author decides):
"Nit: Could rename `proc` to `processPayment` for clarity.
 Not a blocker -- feel free to take or leave."

"Optional: We could use an enum here instead of string constants.
 Happy to merge as-is if you prefer."

Use prefixes:
  "Bug:"      -- Must fix
  "Security:" -- Must fix
  "Nit:"      -- Nice to have
  "Optional:" -- Author's choice
  "Question:" -- Asking for understanding
```

#### 5. Praise Good Code

Reviews should not be only about problems. Call out things the author did well.

```
"Nice use of the builder pattern here. It makes the test
 setup much more readable than the previous approach."

"Great test coverage! The edge case for empty lists
 is exactly the kind of thing that catches real bugs."

"I learned something from this approach. I hadn't
 considered using Optional.flatMap() for this case."
```

---

## Receiving Feedback: Checking Your Ego

Receiving code review feedback is hard. Your code is a reflection of your thinking, and criticism can feel personal. Here is how to handle it well:

### Principles for Receiving Feedback

```
HOW TO RECEIVE FEEDBACK WELL:

  1. ASSUME GOOD INTENT
     The reviewer is trying to make the code better,
     not attack you personally.

  2. SEPARATE CODE FROM IDENTITY
     "This code could be clearer" is not
     "You are not a good developer."

  3. ASK QUESTIONS, DON'T DEFEND
     If you disagree, ask: "Can you explain why
     you prefer that approach?" -- not "My way is fine."

  4. SAY THANK YOU
     "Good catch, I missed that edge case."
     "I hadn't thought of that approach, thanks!"

  5. PICK YOUR BATTLES
     If the suggestion is minor and you have no strong
     opinion, just accept it. Save your energy for
     things that matter.
```

### How to Respond to Different Types of Comments

```
TYPE: Bug report
  Comment: "This will NPE when email is null."
  Response: "Good catch! Fixed in the latest commit."

TYPE: Design suggestion
  Comment: "Have you considered using a strategy pattern here?"
  Response: "Interesting idea. I went with the switch because
             there are only two cases today. If we add more,
             I agree the strategy pattern would be better.
             Want me to refactor now or add a TODO?"

TYPE: Nit
  Comment: "Nit: rename `x` to `orderTotal`."
  Response: "Done." (No need for a long discussion.)

TYPE: Disagreement
  Comment: "I think we should use inheritance here."
  Response: "I chose composition because [specific reason].
             But I see the inheritance angle. Let's discuss
             in standup if you feel strongly about it."
```

---

## Pull Request Size: Smaller Is Better

The single most impactful thing you can do for code review quality is to keep pull requests small.

```
PR SIZE AND REVIEW QUALITY:

  Lines Changed    Review Quality    Time to Review
  +-------------+------------------+------------------+
  |    < 100    | Thorough,        | 15-30 minutes    |
  |             | catches bugs     |                  |
  +-------------+------------------+------------------+
  |  100 - 300  | Good, some       | 30-60 minutes    |
  |             | things missed    |                  |
  +-------------+------------------+------------------+
  |  300 - 500  | Surface-level,   | 60-90 minutes    |
  |             | many things      |                  |
  |             | missed           |                  |
  +-------------+------------------+------------------+
  |    > 500    | "LGTM" stamp,    | 2 minutes        |
  |             | nothing actually | (reviewer gives  |
  |             | reviewed         |  up)             |
  +-------------+------------------+------------------+

  The sweet spot: 100-300 lines changed.
  Anything over 500 lines is almost never reviewed properly.
```

### Strategies for Keeping PRs Small

1. **One concern per PR.** A PR should do one thing: fix one bug, add one feature, or refactor one area.
2. **Separate refactoring from features.** If you need to refactor before adding a feature, make two PRs: one for the refactoring, one for the feature.
3. **Stack PRs.** Break a large feature into sequential PRs that each build on the last.
4. **Ship the skeleton first.** Create the interfaces and structure first, then fill in the implementation.

```
STACKING PRs:

  Instead of one massive PR:

  +------------------------------------------+
  | PR #42: Add checkout feature             |
  | - New database tables                    |
  | - Repository classes                     |
  | - Service layer                          |
  | - Controller                             |
  | - Frontend changes                       |
  | - Tests                                  |
  | 1,200 lines changed                      |
  +------------------------------------------+

  Stack smaller PRs:

  PR #42: Add checkout database schema (80 lines)
                |
  PR #43: Add checkout repository + tests (120 lines)
                |
  PR #44: Add checkout service + tests (150 lines)
                |
  PR #45: Add checkout controller + tests (100 lines)
                |
  PR #46: Add checkout frontend (200 lines)

  Each PR is reviewable. Each can be merged independently.
```

---

## The Code Review Checklist

Use this checklist when reviewing a pull request:

```
CODE REVIEW CHECKLIST:

  FUNCTIONALITY:
  [ ] Code does what the PR description says it does
  [ ] Edge cases are handled (null, empty, boundary values)
  [ ] Error paths are handled appropriately
  [ ] No unintended side effects

  DESIGN:
  [ ] Follows existing patterns in the codebase
  [ ] No unnecessary complexity or over-engineering
  [ ] Responsibilities are in the right places
  [ ] Dependencies point in the right direction

  READABILITY:
  [ ] Names are clear and descriptive
  [ ] Complex logic has explanatory comments
  [ ] Methods are focused (single responsibility)
  [ ] No dead code or commented-out code

  TESTING:
  [ ] New code has tests
  [ ] Tests cover happy path AND error paths
  [ ] Tests are readable and maintainable
  [ ] Edge cases are tested

  SECURITY:
  [ ] User input is validated and sanitized
  [ ] No hardcoded secrets or credentials
  [ ] Authentication/authorization is enforced
  [ ] No SQL injection or XSS vulnerabilities

  PERFORMANCE:
  [ ] No obvious N+1 query issues
  [ ] Large collections are not loaded entirely into memory
  [ ] No unnecessary database calls in loops

  PR QUALITY:
  [ ] PR description explains WHAT and WHY
  [ ] PR is a reasonable size (< 300 lines ideal)
  [ ] Related changes are grouped logically
  [ ] No unrelated changes mixed in
```

---

## Automated Checks: Let Robots Handle the Boring Stuff

Automated checks handle consistency and style so reviewers can focus on logic, design, and correctness.

```
WHAT TO AUTOMATE vs WHAT HUMANS DO:

  AUTOMATE (CI/CD pipeline):            HUMAN REVIEW:
  +------------------------------+     +----------------------------+
  | - Code formatting            |     | - Business logic           |
  | - Linting rules              |     |   correctness              |
  | - Import ordering            |     | - Design decisions         |
  | - Unit test execution        |     | - Architecture fit         |
  | - Code coverage thresholds   |     | - Naming clarity           |
  | - Static analysis            |     | - Error handling strategy  |
  | - Dependency vulnerability   |     | - Performance concerns     |
  |   scanning                   |     | - Security review          |
  | - Build verification         |     | - Knowledge sharing        |
  | - Type checking              |     | - Mentoring and teaching   |
  +------------------------------+     +----------------------------+
```

### Setting Up Automated Checks

```
CI/CD PIPELINE FOR CODE REVIEW:

  Developer pushes PR
         |
         v
  +------------------+
  | 1. Lint           |  Checks naming, style, import order
  +------------------+
         |
         v
  +------------------+
  | 2. Format Check   |  Verifies code is formatted
  +------------------+
         |
         v
  +------------------+
  | 3. Build          |  Compiles and resolves dependencies
  +------------------+
         |
         v
  +------------------+
  | 4. Unit Tests     |  Runs all tests, reports coverage
  +------------------+
         |
         v
  +------------------+
  | 5. Static Analysis|  FindBugs, SonarQube, mypy, etc.
  +------------------+
         |
         v
  +------------------+
  | 6. Security Scan  |  Dependency vulnerabilities
  +------------------+
         |
  All pass? --> Human review begins
  Any fail? --> Author fixes before review
```

### Java CI Example

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: [pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Format check
        run: mvn spotless:check

      - name: Build and test
        run: mvn verify

      - name: Static analysis
        run: mvn spotbugs:check

      - name: Coverage check
        run: |
          mvn jacoco:report
          # Fail if coverage drops below 80%
```

### Python CI Example

```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: [pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Format check
        run: black --check .

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Tests with coverage
        run: pytest --cov=src --cov-fail-under=80
```

---

## Code Review Workflow

A healthy code review workflow looks like this:

```
CODE REVIEW WORKFLOW:

  1. AUTHOR prepares:
     - Write clean, small PR (< 300 lines)
     - Add description: WHAT changed, WHY, HOW to test
     - Self-review before requesting reviews
     - Ensure CI passes

  2. REVIEWER reviews:
     - Read the PR description first
     - Understand the context and goal
     - Review the code, focusing on the pyramid
     - Leave clear, constructive comments
     - Approve, request changes, or comment

  3. AUTHOR responds:
     - Address all comments
     - Fix blocking issues
     - Discuss non-blocking suggestions
     - Request re-review if changes were significant

  4. MERGE:
     - All reviewers approve
     - CI passes
     - Squash or merge per team convention

  Timeline goal: Review within 24 hours of request.
  Stale PRs lose context and become harder to review.
```

### Writing a Good PR Description

```
PR DESCRIPTION TEMPLATE:

  ## What
  Brief description of what this PR does.

  ## Why
  Why this change is needed. Link to issue/ticket.

  ## How
  High-level approach. What alternatives were considered?

  ## Testing
  How was this tested? What scenarios were covered?

  ## Screenshots (if UI change)
  Before and after screenshots.

  ## Checklist
  - [ ] Tests added
  - [ ] Documentation updated
  - [ ] No breaking changes
```

---

## Common Mistakes

### Mistake 1: Rubber-Stamp Reviews

Approving PRs without reading them. This defeats the entire purpose of code review.

**Fix:** Set a minimum review time expectation. If a PR took hours to write, it deserves more than 30 seconds of review.

### Mistake 2: Nitpicking Without Substance

Leaving 20 comments about formatting while missing a critical bug.

**Fix:** Use the review priority pyramid. Automate style checks. Focus on logic and design.

### Mistake 3: Gatekeeping

One senior developer blocks all PRs with personal preferences disguised as "standards."

**Fix:** Document standards explicitly. If it is not in the style guide, it is a preference, not a requirement. Preferences should be suggestions, not blockers.

### Mistake 4: Enormous PRs

PRs with 1,000+ lines that nobody can actually review properly.

**Fix:** Set a soft limit (e.g., 300 lines). If a PR is larger, the author must explain why and consider splitting it.

### Mistake 5: Delayed Reviews

PRs sitting for days without review, losing context and blocking the author.

**Fix:** Set a team SLA (e.g., first review within 24 hours). Use a rotation or assign reviewers proactively.

---

## Best Practices

1. **Automate style and formatting.** Never argue about tabs vs spaces again. Let the formatter decide.
2. **Keep PRs small.** Under 300 lines is ideal. Over 500 lines is a red flag.
3. **Review within 24 hours.** Stale PRs lose context and block other work.
4. **Comment on the code, not the person.** Always assume good intent.
5. **Explain the WHY.** A comment that explains reasoning teaches more than a comment that just says "change this."
6. **Distinguish blocking from non-blocking.** Use prefixes like "Bug:", "Nit:", "Optional:" to set expectations.
7. **Praise good work.** Reviews should not be only about problems.
8. **Self-review before requesting.** Read your own PR as if someone else wrote it. You will catch obvious issues.
9. **Write clear PR descriptions.** Tell reviewers what, why, and how to test.
10. **Rotate reviewers.** Spread knowledge across the team. Everyone should review and be reviewed.

---

## Quick Summary

```
CODE REVIEW CULTURE AT A GLANCE:

  Purpose:  Knowledge sharing, consistency, quality, team ownership

  Focus:    Logic and bugs > Design > Readability > Style

  PR Size:  < 300 lines ideal, > 500 lines is a red flag

  Feedback: Constructive, explains WHY, asks questions,
            comments on code not person

  Automate: Formatting, linting, tests, static analysis

  Timeline: First review within 24 hours
```

---

## Key Points

- Code review is primarily about knowledge sharing and consistency, not just bug catching.
- Focus review energy on correctness, security, and design. Automate style checks.
- Give feedback that is constructive, specific, and explains the reasoning.
- Receive feedback with curiosity, not defensiveness. Assume good intent.
- Keep pull requests under 300 lines for thorough reviews. Over 500 lines means reviewers give up.
- Use prefixes (Bug, Nit, Optional) to distinguish blocking from non-blocking comments.
- Automate everything that can be automated: formatting, linting, tests, static analysis, security scans.
- Review within 24 hours. Stale PRs lose context and block progress.
- Write clear PR descriptions that explain what, why, and how to test.
- Praise good code. Reviews should recognize excellent work, not just problems.

---

## Practice Questions

1. A developer on your team submits a 1,500-line PR that adds a complete new feature. The code looks correct, but you cannot review it thoroughly. What do you do?

2. You receive a review comment that says "This is wrong." No explanation, no suggestion. How do you respond constructively?

3. Your team spends 40% of review time debating code formatting (tabs vs spaces, brace placement). How would you eliminate these debates?

4. A junior developer's PR has correct logic but uses a different pattern than the rest of the codebase. How do you give feedback that teaches without discouraging?

5. Your team has no code review process. Management says it would "slow things down." What arguments would you make for introducing code reviews?

---

## Exercises

### Exercise 1: Review This Code

Review the following code and write review comments. For each comment, indicate whether it is blocking or non-blocking, and explain why.

```java
public class UserService {
    public User createUser(String name, String email, String pw) {
        User u = new User();
        u.setName(name);
        u.setEmail(email);
        u.setPassword(pw);  // stored as plain text
        db.save(u);
        try {
            emailService.sendWelcome(email);
        } catch (Exception e) {
            // ignore
        }
        return u;
    }
}
```

### Exercise 2: Rewrite These Comments

Rewrite these code review comments to be constructive and helpful:

1. "This is terrible code."
2. "Why would you use a for loop here?"
3. "You obviously didn't test this."
4. "This is not how we do things."
5. "Wrong."

### Exercise 3: Set Up Automated Checks

Configure a CI pipeline for a project of your choice that runs the following checks on every PR: code formatting verification, linting, unit tests with coverage reporting (minimum 80%), and static analysis. Document which tools you chose and why.

---

## What Is Next?

With a strong code review culture in place, the next chapter tackles one of the hardest challenges in software development: working with Legacy Code. You will learn techniques for safely modifying code you did not write and do not fully understand -- characterization tests, the strangler fig pattern, branch by abstraction, and more.
