# Chapter 12: Mediator Pattern

## What You Will Learn

- What the Mediator pattern is and why it exists
- How many-to-many communication creates tangled code
- How to build a central mediator that coordinates communication
- How to implement a chat room using the Mediator pattern
- How to build a form mediator where fields react to each other
- The differences between Mediator and Pub/Sub
- When the mediator itself becomes too complex and what to do about it

## Why This Chapter Matters

Imagine a busy airport with dozens of planes in the sky. What if every pilot had to talk directly to every other pilot to avoid collisions? That would be chaos. Instead, airports use air traffic controllers. Every pilot talks to the controller, and the controller coordinates everyone.

This is exactly the problem you face in frontend development. When you have a chat room with multiple users, a form where fields depend on each other, or a dialog with multiple interactive sections, direct communication between every component becomes a nightmare to maintain.

The Mediator pattern gives you that air traffic controller for your code.

---

## The Problem: Many-to-Many Communication

Let us start with a real problem. You are building a chat room. You have multiple users who need to send messages to each other.

### The Naive Approach (Direct Communication)

```javascript
// Without Mediator - every user knows about every other user

class User {
  constructor(name) {
    this.name = name;
    this.otherUsers = []; // Must track ALL other users
  }

  addContact(user) {
    this.otherUsers.push(user);
  }

  sendMessage(message) {
    // Must loop through ALL contacts and send individually
    this.otherUsers.forEach(user => {
      user.receiveMessage(message, this.name);
    });
  }

  receiveMessage(message, fromUser) {
    console.log(`${this.name} received from ${fromUser}: ${message}`);
  }
}

// Setting up connections is painful
const alice = new User('Alice');
const bob = new User('Bob');
const charlie = new User('Charlie');

// Every user must know about every other user
alice.addContact(bob);
alice.addContact(charlie);
bob.addContact(alice);
bob.addContact(charlie);
charlie.addContact(alice);
charlie.addContact(bob);

alice.sendMessage('Hello everyone!');
```

**Output:**
```
Bob received from Alice: Hello everyone!
Charlie received from Alice: Hello everyone!
```

### What Is Wrong With This?

Look at the connections required:

```
Direct Communication (3 users):

    Alice <-------> Bob
      ^              ^
      |              |
      v              v
    Charlie <------> (needs connection to both)

    Connections needed: 3

Direct Communication (5 users):

    Alice <-> Bob
    Alice <-> Charlie
    Alice <-> Diana
    Alice <-> Eve
    Bob <-> Charlie
    Bob <-> Diana
    Bob <-> Eve
    Charlie <-> Diana
    Charlie <-> Eve
    Diana <-> Eve

    Connections needed: 10
```

The formula for connections is `n * (n - 1) / 2`. With 10 users, you need 45 connections. With 20 users, you need 190. This grows very fast.

Every time you add a new user, you must update every existing user. Every user depends on every other user. Testing one user means setting up all the others.

---

## The Solution: Central Mediator

Instead of everyone talking to everyone, everyone talks to one central point: the mediator.

```
With Mediator:

    Alice ----\
               \
    Bob -------> Mediator (Chat Room)
               /
    Charlie --/

    Connections needed: 3 (always equals number of users)
```

Think of it like this:

| Situation | Without Mediator | With Mediator |
|-----------|-----------------|---------------|
| Airport | Pilots talk to each other | Pilots talk to control tower |
| Chat | Users message each user | Users message chat room |
| Form | Fields check every other field | Fields report to form manager |
| Game | Players interact directly | Players interact through game engine |

---

## Building a Chat Room Mediator

Let us build this step by step.

### Step 1: Create the Mediator (Chat Room)

```javascript
// The mediator - coordinates all communication
class ChatRoom {
  constructor() {
    this.users = new Map(); // Track all users by name
  }

  // Register a user with the chat room
  register(user) {
    this.users.set(user.name, user);
    user.chatRoom = this; // Give user a reference to the mediator
    console.log(`${user.name} joined the chat room`);
  }

  // The core mediator method - routes messages
  sendMessage(message, fromUser, toUser) {
    if (toUser) {
      // Private message - send to specific user
      const recipient = this.users.get(toUser);
      if (recipient) {
        recipient.receiveMessage(message, fromUser);
      } else {
        console.log(`User ${toUser} not found`);
      }
    } else {
      // Broadcast - send to everyone except sender
      this.users.forEach((user, name) => {
        if (name !== fromUser) {
          user.receiveMessage(message, fromUser);
        }
      });
    }
  }
}
```

**Line-by-line explanation:**

- `this.users = new Map()` - The mediator keeps track of all participants. A Map gives us fast lookup by name.
- `register(user)` - When a user joins, we store them and give them a reference back to the mediator. This is the only connection each user needs.
- `sendMessage(message, fromUser, toUser)` - This is the heart of the mediator. It decides how to route messages. If `toUser` is specified, it sends a private message. Otherwise, it broadcasts to everyone except the sender.

### Step 2: Create the User (Colleague)

```javascript
// The colleague - only knows about the mediator, not other users
class ChatUser {
  constructor(name) {
    this.name = name;
    this.chatRoom = null; // Will be set when registered
    this.messageLog = [];
  }

  // Send a message through the mediator
  send(message, toUser) {
    console.log(`${this.name} sends: ${message}`);
    this.chatRoom.sendMessage(message, this.name, toUser);
  }

  // Receive a message (called by the mediator)
  receiveMessage(message, fromUser) {
    const entry = `${fromUser}: ${message}`;
    this.messageLog.push(entry);
    console.log(`[${this.name}'s screen] ${entry}`);
  }
}
```

**Line-by-line explanation:**

- `this.chatRoom = null` - The user does not know about other users. It only has a reference to the mediator (chat room).
- `send(message, toUser)` - Instead of finding and calling other users directly, the user asks the mediator to deliver the message.
- `receiveMessage(message, fromUser)` - The mediator calls this method when a message arrives. The user does not know or care who else is in the chat.

### Step 3: Use It

```javascript
// Create the mediator
const chatRoom = new ChatRoom();

// Create users
const alice = new ChatUser('Alice');
const bob = new ChatUser('Bob');
const charlie = new ChatUser('Charlie');

// Register users with the mediator
chatRoom.register(alice);
chatRoom.register(bob);
chatRoom.register(charlie);

// Alice broadcasts to everyone
alice.send('Good morning, team!');

console.log('---');

// Bob sends a private message to Alice
bob.send('Hey Alice, got a minute?', 'Alice');

console.log('---');

// Charlie broadcasts
charlie.send('Meeting starts in 5 minutes');
```

**Output:**
```
Alice joined the chat room
Bob joined the chat room
Charlie joined the chat room
Alice sends: Good morning, team!
[Bob's screen] Alice: Good morning, team!
[Charlie's screen] Alice: Good morning, team!
---
Bob sends: Hey Alice, got a minute?
[Alice's screen] Bob: Hey Alice, got a minute?
---
Charlie sends: Meeting starts in 5 minutes
[Alice's screen] Charlie: Meeting starts in 5 minutes
[Bob's screen] Charlie: Meeting starts in 5 minutes
```

### The Key Difference

```
BEFORE (without mediator):
- Alice must know about Bob AND Charlie
- Bob must know about Alice AND Charlie
- Adding Diana means updating Alice, Bob, AND Charlie

AFTER (with mediator):
- Alice only knows about ChatRoom
- Bob only knows about ChatRoom
- Adding Diana means registering her with ChatRoom (one change)
```

---

## Real-World Example: Form Mediator

Forms are one of the most common places where the Mediator pattern shines. Imagine a shipping form where:

- Selecting "International" shipping shows a customs field
- Entering a country updates the tax rate
- Selecting "Express" shipping disables certain payment methods
- The submit button enables only when all required fields are valid

Without a mediator, every field would need to know about every other field. With a mediator, each field reports to the form mediator, and the mediator decides what to update.

### Building the Form Mediator

```javascript
// Form Mediator - coordinates all field interactions
class FormMediator {
  constructor() {
    this.fields = {};
    this.rules = [];
  }

  // Register a form field
  registerField(name, field) {
    this.fields[name] = field;
    field.mediator = this;
  }

  // Add a coordination rule
  addRule(rule) {
    this.rules.push(rule);
  }

  // Called when any field changes - this is the mediator logic
  fieldChanged(fieldName, value) {
    console.log(`Field "${fieldName}" changed to: ${value}`);

    // Run all rules to determine what else should change
    this.rules.forEach(rule => {
      rule(fieldName, value, this.fields);
    });

    // Check if form is valid
    this.validateForm();
  }

  validateForm() {
    const allValid = Object.values(this.fields)
      .filter(f => f.required && f.visible)
      .every(f => f.isValid());

    if (this.fields.submitButton) {
      this.fields.submitButton.setEnabled(allValid);
    }

    console.log(`Form valid: ${allValid}`);
  }
}
```

**Line-by-line explanation:**

- `this.fields = {}` - Stores all form fields by name, so rules can reference any field.
- `this.rules = []` - Stores functions that define how fields interact. Each rule runs when any field changes.
- `fieldChanged(fieldName, value)` - The core method. When a field changes, the mediator runs all rules and revalidates the form. No field needs to know about any other field.

### The Form Fields

```javascript
// A form field that communicates through the mediator
class FormField {
  constructor(name, options = {}) {
    this.name = name;
    this.value = options.defaultValue || '';
    this.required = options.required || false;
    this.visible = options.visible !== false;
    this.enabled = options.enabled !== false;
    this.mediator = null;
  }

  setValue(value) {
    this.value = value;
    // Tell the mediator about the change - not other fields
    this.mediator.fieldChanged(this.name, value);
  }

  setVisible(visible) {
    this.visible = visible;
    console.log(`  "${this.name}" is now ${visible ? 'visible' : 'hidden'}`);
  }

  setEnabled(enabled) {
    this.enabled = enabled;
    console.log(`  "${this.name}" is now ${enabled ? 'enabled' : 'disabled'}`);
  }

  isValid() {
    if (!this.required || !this.visible) return true;
    return this.value !== '' && this.value !== null;
  }
}
```

### Putting It Together

```javascript
// Create the mediator
const formMediator = new FormMediator();

// Create form fields
const shippingType = new FormField('shippingType', { required: true });
const country = new FormField('country', { required: true });
const customsNumber = new FormField('customsNumber', {
  required: true,
  visible: false
});
const expressOption = new FormField('expressOption');
const paypalOption = new FormField('paypalOption');
const submitButton = new FormField('submitButton');

// Register all fields with the mediator
formMediator.registerField('shippingType', shippingType);
formMediator.registerField('country', country);
formMediator.registerField('customsNumber', customsNumber);
formMediator.registerField('expressOption', expressOption);
formMediator.registerField('paypalOption', paypalOption);
formMediator.registerField('submitButton', submitButton);

// Define rules - the coordination logic lives in the mediator
formMediator.addRule((fieldName, value, fields) => {
  // Rule 1: Show customs field for international shipping
  if (fieldName === 'shippingType') {
    const isInternational = value === 'international';
    fields.customsNumber.setVisible(isInternational);
  }
});

formMediator.addRule((fieldName, value, fields) => {
  // Rule 2: Disable PayPal for express shipping
  if (fieldName === 'expressOption') {
    const isExpress = value === 'express';
    fields.paypalOption.setEnabled(!isExpress);
  }
});

// Simulate user filling out the form
console.log('=== User selects International shipping ===');
shippingType.setValue('international');

console.log('\n=== User enters country ===');
country.setValue('Canada');

console.log('\n=== User selects Express shipping ===');
expressOption.setValue('express');
```

**Output:**
```
=== User selects International shipping ===
Field "shippingType" changed to: international
  "customsNumber" is now visible
Form valid: false

=== User enters country ===
Field "country" changed to: Canada
Form valid: false

=== User selects Express shipping ===
Field "expressOption" changed to: express
  "paypalOption" is now disabled
Form valid: false
```

The form stays invalid because `customsNumber` is now visible and required but empty. Once the user fills it in, the form becomes valid.

---

## Form Mediator in React

Let us see how this pattern looks in a React application.

```jsx
import React, { useState, useCallback } from 'react';

// The mediator logic lives in a custom hook
function useFormMediator() {
  const [formState, setFormState] = useState({
    shippingType: '',
    country: '',
    customsNumber: '',
    expressShipping: false,
    paymentMethod: 'credit-card',
  });

  const [fieldVisibility, setFieldVisibility] = useState({
    customsNumber: false,
  });

  const [fieldEnabled, setFieldEnabled] = useState({
    paypalOption: true,
  });

  // The mediator function - coordinates all changes
  const updateField = useCallback((fieldName, value) => {
    // Update the field value
    setFormState(prev => ({ ...prev, [fieldName]: value }));

    // Apply coordination rules
    if (fieldName === 'shippingType') {
      // Rule: Show customs field for international shipping
      setFieldVisibility(prev => ({
        ...prev,
        customsNumber: value === 'international',
      }));
    }

    if (fieldName === 'expressShipping') {
      // Rule: Disable PayPal for express shipping
      setFieldEnabled(prev => ({
        ...prev,
        paypalOption: !value,
      }));
    }
  }, []);

  // Check form validity
  const isFormValid = formState.shippingType !== ''
    && formState.country !== ''
    && (!fieldVisibility.customsNumber || formState.customsNumber !== '');

  return {
    formState,
    fieldVisibility,
    fieldEnabled,
    updateField,
    isFormValid,
  };
}

// The form component - fields do NOT talk to each other
function ShippingForm() {
  const {
    formState,
    fieldVisibility,
    fieldEnabled,
    updateField,
    isFormValid,
  } = useFormMediator();

  return (
    <form>
      <h2>Shipping Details</h2>

      <label>Shipping Type:</label>
      <select
        value={formState.shippingType}
        onChange={(e) => updateField('shippingType', e.target.value)}
      >
        <option value="">Select...</option>
        <option value="domestic">Domestic</option>
        <option value="international">International</option>
      </select>

      <label>Country:</label>
      <input
        type="text"
        value={formState.country}
        onChange={(e) => updateField('country', e.target.value)}
      />

      {fieldVisibility.customsNumber && (
        <>
          <label>Customs Number:</label>
          <input
            type="text"
            value={formState.customsNumber}
            onChange={(e) => updateField('customsNumber', e.target.value)}
          />
        </>
      )}

      <label>
        <input
          type="checkbox"
          checked={formState.expressShipping}
          onChange={(e) => updateField('expressShipping', e.target.checked)}
        />
        Express Shipping
      </label>

      <label>Payment Method:</label>
      <select
        value={formState.paymentMethod}
        onChange={(e) => updateField('paymentMethod', e.target.value)}
      >
        <option value="credit-card">Credit Card</option>
        <option value="paypal" disabled={!fieldEnabled.paypalOption}>
          PayPal {!fieldEnabled.paypalOption && '(not available with Express)'}
        </option>
      </select>

      <button type="submit" disabled={!isFormValid}>
        Place Order
      </button>
    </form>
  );
}
```

**How the mediator works in React:**

```
Field Change Flow:

  User changes       updateField()         State updates
  "shippingType" --> (mediator logic) --> fieldVisibility changes
       |                                  formState changes
       |                                       |
       v                                       v
  Only this field      React re-renders    Other fields
  calls updateField    the component        show/hide/
                                           enable/disable
```

Each field only calls `updateField`. It does not know about any other field. The `useFormMediator` hook is the mediator that decides what else should change.

---

## Real-World Use Case: Dialog Coordination

Dialogs (modals) with multiple sections are another common use case. Imagine a settings dialog where changing one option affects what other options are available.

```javascript
// Dialog Mediator
class DialogMediator {
  constructor() {
    this.sections = {};
    this.state = {};
  }

  registerSection(name, section) {
    this.sections[name] = section;
    section.mediator = this;
  }

  notify(sectionName, event, data) {
    console.log(`[Dialog] ${sectionName} triggered: ${event}`);

    switch (event) {
      case 'theme-changed':
        // When theme changes, update preview and reset custom colors
        if (this.sections.preview) {
          this.sections.preview.updateTheme(data.theme);
        }
        if (data.theme !== 'custom' && this.sections.colors) {
          this.sections.colors.disable();
        }
        if (data.theme === 'custom' && this.sections.colors) {
          this.sections.colors.enable();
        }
        break;

      case 'font-size-changed':
        // When font size changes, warn if too large for mobile
        if (this.sections.preview) {
          this.sections.preview.updateFontSize(data.size);
        }
        if (data.size > 24 && this.sections.warnings) {
          this.sections.warnings.show('Large fonts may not display well on mobile');
        }
        break;

      case 'section-collapsed':
        // When a section collapses, expand the next one
        const sectionNames = Object.keys(this.sections);
        const currentIndex = sectionNames.indexOf(sectionName);
        const nextSection = this.sections[sectionNames[currentIndex + 1]];
        if (nextSection && nextSection.expand) {
          nextSection.expand();
        }
        break;
    }
  }
}
```

---

## Real-World Use Case: Wizard Steps

Multi-step wizards are a perfect fit for the Mediator pattern. Each step needs to know about the state of other steps, but with a mediator, each step only talks to the wizard controller.

```jsx
import React, { useState, useCallback } from 'react';

function useWizardMediator(steps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepData, setStepData] = useState({});
  const [stepValidity, setStepValidity] = useState(
    steps.reduce((acc, step) => ({ ...acc, [step.id]: false }), {})
  );

  // Mediator: handle step completion
  const completeStep = useCallback((stepId, data) => {
    setStepData(prev => ({ ...prev, [stepId]: data }));
    setStepValidity(prev => ({ ...prev, [stepId]: true }));

    // Automatically advance to next step
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  }, [steps.length]);

  // Mediator: check if user can skip to a step
  const canGoToStep = useCallback((targetStep) => {
    // Can only go to steps where all previous steps are valid
    for (let i = 0; i < targetStep; i++) {
      if (!stepValidity[steps[i].id]) return false;
    }
    return true;
  }, [stepValidity, steps]);

  // Mediator: get data from a previous step
  const getStepData = useCallback((stepId) => {
    return stepData[stepId] || {};
  }, [stepData]);

  return {
    currentStep,
    setCurrentStep,
    completeStep,
    canGoToStep,
    getStepData,
    isComplete: Object.values(stepValidity).every(Boolean),
  };
}

// Usage
function CheckoutWizard() {
  const steps = [
    { id: 'address', title: 'Shipping Address' },
    { id: 'shipping', title: 'Shipping Method' },
    { id: 'payment', title: 'Payment' },
    { id: 'review', title: 'Review Order' },
  ];

  const wizard = useWizardMediator(steps);

  // Each step component only talks to the wizard mediator
  // It does not know about other steps
  return (
    <div className="wizard">
      <div className="wizard-steps">
        {steps.map((step, index) => (
          <button
            key={step.id}
            onClick={() => wizard.canGoToStep(index) && wizard.setCurrentStep(index)}
            disabled={!wizard.canGoToStep(index)}
            className={index === wizard.currentStep ? 'active' : ''}
          >
            {step.title}
          </button>
        ))}
      </div>

      <div className="wizard-content">
        {wizard.currentStep === 0 && (
          <AddressStep
            onComplete={(data) => wizard.completeStep('address', data)}
          />
        )}
        {wizard.currentStep === 1 && (
          <ShippingStep
            address={wizard.getStepData('address')}
            onComplete={(data) => wizard.completeStep('shipping', data)}
          />
        )}
        {wizard.currentStep === 2 && (
          <PaymentStep
            onComplete={(data) => wizard.completeStep('payment', data)}
          />
        )}
        {wizard.currentStep === 3 && (
          <ReviewStep
            allData={{
              ...wizard.getStepData('address'),
              ...wizard.getStepData('shipping'),
              ...wizard.getStepData('payment'),
            }}
          />
        )}
      </div>
    </div>
  );
}
```

**How the wizard mediator coordinates steps:**

```
Step Flow:

  AddressStep               WizardMediator            ShippingStep
      |                          |                         |
      |-- completeStep(data) --> |                         |
      |                          |-- setCurrentStep(1) --> |
      |                          |-- passes address   --> |
      |                          |   data as props         |
      |                          |                         |
      |                          | <-- completeStep(data) -|
      |                          |-- setCurrentStep(2) -->
```

Each step only knows about the mediator. The `AddressStep` does not import or reference `ShippingStep`. The mediator handles all the coordination.

---

## Mediator vs Pub/Sub: What Is the Difference?

These patterns look similar but have an important difference.

```
Mediator:
- Has LOGIC about how to coordinate
- Knows about specific participants
- Makes decisions about what happens

    Component A ---> Mediator ---> Component B
                    (decides      (mediator calls
                     what to do)   B directly)

Pub/Sub:
- Is a DUMB message bus
- Does NOT know about specific participants
- Just passes messages along

    Component A ---> Event Bus ---> Component B
                    (just routes    (subscribed to
                     messages)      that event)
```

| Feature | Mediator | Pub/Sub |
|---------|----------|---------|
| Intelligence | Contains business logic | No logic, just routing |
| Participant awareness | Knows its participants | Does not know subscribers |
| Control flow | Mediator decides what happens | Publishers do not know who listens |
| Coupling | Participants coupled to mediator | Loose coupling through events |
| Complexity | Logic centralized in mediator | Logic distributed in handlers |

### Concrete Example

```javascript
// MEDIATOR approach - the mediator contains the logic
class LoginMediator {
  notify(sender, event) {
    if (event === 'login-success') {
      // Mediator DECIDES what happens next
      this.userPanel.showWelcome(sender.username);
      this.navbar.showUserMenu();
      this.chatWidget.connect(sender.userId);
      this.notificationService.fetchUnread(sender.userId);
    }
  }
}

// PUB/SUB approach - no central logic
loginService.publish('login-success', { userId: 123, username: 'Alice' });

// Each subscriber decides independently what to do
eventBus.subscribe('login-success', (data) => {
  userPanel.showWelcome(data.username);
});
eventBus.subscribe('login-success', (data) => {
  navbar.showUserMenu();
});
eventBus.subscribe('login-success', (data) => {
  chatWidget.connect(data.userId);
});
```

With the Mediator, the coordination logic is in one place. With Pub/Sub, it is spread across subscribers. Neither is always better; they solve different problems.

---

## When the Mediator Becomes Too Complex

One danger of the Mediator pattern is that the mediator can grow into a "god object" that knows too much and does too much.

### Signs Your Mediator Is Too Complex

```javascript
// BAD: Mediator doing too much
class GodMediator {
  notify(sender, event, data) {
    // 500+ lines of switch/case statements
    switch (event) {
      case 'user-login':
        // 30 lines of logic
        break;
      case 'user-logout':
        // 25 lines of logic
        break;
      case 'item-added':
        // 40 lines of logic
        break;
      // ... 50 more cases
    }
  }
}
```

### How to Fix It: Split the Mediator

```javascript
// GOOD: Split into focused mediators

class AuthMediator {
  // Only handles authentication-related coordination
  notify(sender, event, data) {
    switch (event) {
      case 'login':
        this.userPanel.showWelcome(data.username);
        this.navbar.showUserMenu();
        break;
      case 'logout':
        this.userPanel.showLogin();
        this.navbar.showGuestMenu();
        break;
    }
  }
}

class CartMediator {
  // Only handles shopping cart coordination
  notify(sender, event, data) {
    switch (event) {
      case 'item-added':
        this.cartIcon.updateCount(data.count);
        this.priceDisplay.recalculate();
        break;
      case 'item-removed':
        this.cartIcon.updateCount(data.count);
        this.priceDisplay.recalculate();
        if (data.count === 0) {
          this.checkoutButton.disable();
        }
        break;
    }
  }
}
```

### Rule of Thumb

If your mediator has more than 5 to 7 event types, consider splitting it. Each mediator should handle one area of coordination.

```
BEFORE (one giant mediator):

  Auth ----\
  Cart -----> God Mediator (handles everything)
  Chat ----/
  Nav  ---/

AFTER (focused mediators):

  Auth -------> AuthMediator
  Cart -------> CartMediator
  Chat -------> ChatMediator
  Nav  -------> NavMediator
```

---

## When to Use / When NOT to Use

### Use the Mediator Pattern When

1. **Multiple components need to communicate** - Chat rooms, collaborative editors, game state
2. **Form fields depend on each other** - Show/hide, enable/disable based on other fields
3. **Dialog sections coordinate** - Settings panels, wizard steps
4. **You want to centralize complex coordination logic** - Instead of spreading it across many components
5. **Adding new participants should be easy** - Just register them with the mediator

### Do NOT Use the Mediator Pattern When

1. **Only two components communicate** - Direct communication is simpler
2. **Communication is one-way** - Use simple props or callbacks instead
3. **There is no coordination logic** - If you just need event routing, use Pub/Sub
4. **The mediator would have no logic** - It would just be a pass-through (use Pub/Sub instead)
5. **Components are already well-isolated** - Do not add complexity where it is not needed

---

## Common Mistakes

### Mistake 1: Making Everything Go Through the Mediator

```javascript
// BAD: Simple parent-child communication through mediator
class ButtonMediator {
  notify(sender, event) {
    if (event === 'click') {
      this.label.setText('Clicked!');
    }
  }
}

// GOOD: Just use a callback
<Button onClick={() => setLabel('Clicked!')} />
```

If two components have a simple, direct relationship, a mediator adds unnecessary complexity.

### Mistake 2: Letting Participants Know About Each Other

```javascript
// BAD: User still references other users
class ChatUser {
  send(message) {
    // This defeats the purpose of having a mediator
    this.chatRoom.users.forEach(user => {
      if (user !== this) user.receive(message);
    });
  }
}

// GOOD: User only talks to mediator
class ChatUser {
  send(message) {
    this.chatRoom.sendMessage(message, this.name);
  }
}
```

The whole point is that participants only know about the mediator, not about each other.

### Mistake 3: Not Defining Clear Events

```javascript
// BAD: Passing raw data without structure
mediator.notify(this, { type: 'something', data: someData, extra: moreData });

// GOOD: Define clear event types
mediator.notify(this, 'FIELD_CHANGED', { fieldName: 'email', value: 'a@b.com' });
mediator.notify(this, 'STEP_COMPLETED', { stepId: 'address', data: addressData });
```

---

## Best Practices

1. **Keep the mediator focused** - One mediator per area of coordination (auth, cart, chat)
2. **Define clear event types** - Use constants or enums for event names
3. **Participants should not access each other** - They should only know about the mediator
4. **Keep coordination logic in the mediator** - Not in the participants
5. **In React, custom hooks make great mediators** - `useFormMediator`, `useWizardMediator`
6. **Document the rules** - Since all logic is centralized, document what triggers what
7. **Test the mediator independently** - Since all logic is in one place, it is easy to test

---

## Quick Summary

The Mediator pattern replaces many-to-many communication with a central coordinator. Instead of every component talking to every other component, each component only talks to the mediator. The mediator contains the logic for how to coordinate the components. This reduces coupling, makes it easy to add new participants, and centralizes complex interaction logic. In React, custom hooks often serve as mediators for form coordination, wizard steps, and dialog management.

---

## Key Points

- The Mediator pattern introduces a central object that controls communication between other objects
- Without a mediator, N components need N*(N-1)/2 connections; with a mediator, they need only N
- The mediator contains business logic about how to coordinate (unlike Pub/Sub which is a dumb message bus)
- Air traffic controller is the classic analogy: pilots talk to the tower, not to each other
- In React, custom hooks serve as mediators, centralizing state coordination logic
- A mediator that grows too large should be split into focused sub-mediators
- Each participant should only know about the mediator, never about other participants

---

## Practice Questions

1. You have a dashboard with 5 widgets that all need to update when the user changes a date filter. Would you use a Mediator or Pub/Sub pattern? Why?

2. A form has 3 fields: country, state, and city. Selecting a country populates states, and selecting a state populates cities. Draw the communication flow using a mediator.

3. Your mediator class has grown to 800 lines with 20 event types. What would you do to improve this?

4. What is the key difference between a Mediator and an Event Bus (Pub/Sub)?

5. In the chat room example, what would you need to change if you wanted to add a "typing indicator" feature? How does the mediator make this easier?

---

## Exercises

### Exercise 1: Game State Mediator

Build a simple tic-tac-toe game mediator that:
- Tracks whose turn it is
- Validates moves (is the cell empty?)
- Checks for a winner after each move
- Notifies the display to update
- Handles game reset

Hint: The mediator should coordinate between the board, the players, and the display.

### Exercise 2: Notification Center Mediator

Build a notification center mediator in React that:
- Receives notifications from different sources (email, chat, system)
- Applies rules: if "Do Not Disturb" is on, only show urgent notifications
- Groups notifications by source
- Auto-dismisses notifications after a timeout
- Updates the notification badge count

### Exercise 3: Multi-Panel Editor

Build a mediator for a code editor with three panels:
- File tree panel (selecting a file opens it in the editor)
- Code editor panel (editing code updates the preview)
- Preview panel (shows the output)
- When a file is saved, the file tree should show a "saved" indicator

Each panel should only communicate through the mediator.

---

## What Is Next?

Now that you understand how the Mediator pattern centralizes communication between many components, we will explore the Mixin pattern. Mixins solve a different problem: how do you share behavior across unrelated classes without creating deep inheritance chains? You will learn why mixins were popular, why they fell out of favor, and what replaced them in modern React.
