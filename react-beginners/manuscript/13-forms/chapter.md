# Chapter 13: Forms

---

## What You Will Learn

- How forms work in React (and how they are different from regular HTML forms)
- What a controlled component is (React controls the input value)
- How to handle text inputs, textareas, select dropdowns, checkboxes, and radio buttons
- How to handle form submission and prevent the page from refreshing
- How to do simple form validation (checking if a field is empty)
- How to collect multiple form fields into one state object
- How to build a simple contact form

## Why This Chapter Matters

Forms are everywhere on the internet. Every time you sign up for an account, log in, search for something, or fill out a survey, you are using a form. If you want to build real applications, you need to know how forms work in React.

React handles forms differently from plain HTML. In React, your component stays in control of what the user types. This might sound strange at first, but it gives you a lot of power. You can check what the user types as they type it. You can show error messages immediately. You can format their input on the fly.

Let us learn how.

---

## How Forms Work in Regular HTML

Before we look at React, let us quickly understand how forms work in plain HTML.

In regular HTML, the browser keeps track of what the user types. When the user clicks the submit button, the browser collects all the form data and sends it to a server. The page usually refreshes.

```html
<form>
  <input type="text" name="username" />
  <button type="submit">Submit</button>
</form>
```

The browser controls the input. The browser remembers what the user typed.

## How Forms Work in React — Controlled Components

In React, we do things differently. Instead of letting the browser control the input, **React controls the input**. We use state to store the value of the input. When the user types something, we update the state. The input always shows whatever is in the state.

This is called a **controlled component**. The word "controlled" means React is in charge. React tells the input what to display.

Think of it like this:

- **Regular HTML form**: The input is a whiteboard. The user writes on it directly. The whiteboard remembers what was written.
- **React controlled form**: The input is a TV screen. The user types on a keyboard, but the TV only shows what React tells it to show. React is the one deciding what appears on the screen.

Why would we want this? Because when React controls the input, we always know exactly what the user has typed. We can check it, change it, or validate it at any moment.

---

## Your First Controlled Input

Let us start with a simple text input.

```jsx
import { useState } from 'react';

function NameForm() {
  const [name, setName] = useState('');

  function handleChange(event) {
    setName(event.target.value);
  }

  return (
    <div>
      <label>Your name: </label>
      <input type="text" value={name} onChange={handleChange} />
      <p>Hello, {name}!</p>
    </div>
  );
}

export default NameForm;
```

**What you will see on the screen:**

```
Your name: [___________]
Hello, !
```

As you type "Sara" into the input, you will see:

```
Your name: [Sara_______]
Hello, Sara!
```

### Line-by-Line Explanation

```jsx
const [name, setName] = useState('');
```

We create a state variable called `name`. It starts as an empty string (`''`). This state will hold whatever the user types.

```jsx
function handleChange(event) {
  setName(event.target.value);
}
```

This function runs every time the user types a character. The `event` is an object that React gives us. It contains information about what happened. `event.target` is the input element. `event.target.value` is whatever text is currently in the input. We take that text and put it into our state using `setName`.

```jsx
<input type="text" value={name} onChange={handleChange} />
```

Two important things here:
- `value={name}` — This tells the input to show whatever is in our `name` state. This is what makes it a controlled component. The input does not decide what to show. React decides.
- `onChange={handleChange}` — Every time the user types, call the `handleChange` function.

```jsx
<p>Hello, {name}!</p>
```

This paragraph displays the name in real time. As the state changes, React re-renders, and the greeting updates.

### The Flow of a Controlled Input

Here is what happens step by step when the user types the letter "S":

```
1. User presses "S" on the keyboard
2. React calls the handleChange function
3. handleChange reads event.target.value (which is "S")
4. handleChange calls setName("S")
5. React updates the state to "S"
6. React re-renders the component
7. The input now shows "S" (because value={name} and name is now "S")
8. The paragraph shows "Hello, S!"
```

This happens for every single character the user types. It is very fast. You will not notice any delay.

---

## Handling Form Submission

When a user fills out a form, they usually click a submit button. In React, we need to handle this properly.

```jsx
import { useState } from 'react';

function GreetingForm() {
  const [name, setName] = useState('');
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setSubmitted(true);
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>Enter your name: </label>
      <input
        type="text"
        value={name}
        onChange={(event) => setName(event.target.value)}
      />
      <button type="submit">Submit</button>

      {submitted && <p>Welcome, {name}!</p>}
    </form>
  );
}

export default GreetingForm;
```

**What you will see:**

Before submitting:

```
Enter your name: [Sara_______]  [Submit]
```

After clicking Submit:

```
Enter your name: [Sara_______]  [Submit]
Welcome, Sara!
```

### What Is event.preventDefault()?

This is very important. Let us understand it clearly.

When you submit a form in a browser, the browser's default behavior is to **refresh the entire page** and send the data to a server. That is how forms worked in the old days of the internet.

But in React, we do not want the page to refresh. We want to stay on the same page and handle the data ourselves with JavaScript.

`event.preventDefault()` tells the browser: **"Stop! Do not do what you normally do. Do not refresh the page. I will handle this myself."**

Think of it like this: Imagine you are at a restaurant. When you finish eating, the waiter normally brings you the bill. But you tell the waiter, "Wait, do not bring the bill yet. I want to order dessert first." You are preventing the default action.

If you forget `event.preventDefault()`, the page will refresh, your state will be lost, and your React app will start over from scratch. Always include it when handling form submissions.

### A Shorter Way to Write onChange

Notice that in this example, instead of writing a separate `handleChange` function, we wrote the function directly:

```jsx
onChange={(event) => setName(event.target.value)}
```

This is called an **inline function**. It does the same thing. It is just shorter. Use whichever style you find easier to read.

---

## Textarea in React

In regular HTML, a textarea works like this:

```html
<textarea>Some text here</textarea>
```

The text goes between the opening and closing tags.

In React, a textarea works more like an input. You use the `value` attribute:

```jsx
import { useState } from 'react';

function MessageForm() {
  const [message, setMessage] = useState('');

  return (
    <div>
      <label>Your message:</label>
      <br />
      <textarea
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        rows={4}
        cols={40}
      />
      <p>You typed {message.length} characters.</p>
    </div>
  );
}

export default MessageForm;
```

**What you will see:**

```
Your message:
+--------------------------------------+
| Hello, this is my message            |
|                                      |
|                                      |
|                                      |
+--------------------------------------+
You typed 27 characters.
```

The textarea works exactly like a text input. You use `value` to control it and `onChange` to update the state. The character count updates in real time as you type.

---

## Select Dropdown in React

A select dropdown lets the user choose one option from a list. In React, we control it the same way as inputs.

```jsx
import { useState } from 'react';

function ColorPicker() {
  const [color, setColor] = useState('green');

  return (
    <div>
      <label>Pick your favorite color: </label>
      <select value={color} onChange={(event) => setColor(event.target.value)}>
        <option value="red">Red</option>
        <option value="green">Green</option>
        <option value="blue">Blue</option>
        <option value="yellow">Yellow</option>
      </select>
      <p>You picked: {color}</p>
    </div>
  );
}

export default ColorPicker;
```

**What you will see:**

```
Pick your favorite color: [Green ▼]
You picked: green
```

### How It Works

- `value={color}` — The dropdown shows whichever option matches the state.
- `onChange` — When the user picks a different option, we update the state.
- `useState('green')` — We start with "green" as the default selection.

The pattern is always the same: **state controls the value, onChange updates the state.**

---

## Checkboxes in React

Checkboxes are a little different. Instead of `value`, we use `checked`. A checkbox is either checked (true) or not checked (false). That is a boolean.

```jsx
import { useState } from 'react';

function AgreementForm() {
  const [agreed, setAgreed] = useState(false);

  return (
    <div>
      <label>
        <input
          type="checkbox"
          checked={agreed}
          onChange={(event) => setAgreed(event.target.checked)}
        />
        I agree to the terms and conditions
      </label>

      <br />
      <button disabled={!agreed}>Sign Up</button>

      {agreed && <p>Thank you for agreeing!</p>}
    </div>
  );
}

export default AgreementForm;
```

**What you will see (before checking):**

```
[ ] I agree to the terms and conditions
[Sign Up] (button is grayed out)
```

**After checking the box:**

```
[✓] I agree to the terms and conditions
[Sign Up] (button is now active)
Thank you for agreeing!
```

### Key Differences for Checkboxes

- We use `checked={agreed}` instead of `value={agreed}`.
- We read `event.target.checked` instead of `event.target.value`.
- The state is a boolean (`true` or `false`), not a string.
- `disabled={!agreed}` means the button is disabled when `agreed` is false. The `!` flips true to false and false to true.

---

## Radio Buttons in React

Radio buttons let the user pick **one option** from a group. Only one radio button in a group can be selected at a time. Think of them like the buttons on an old car radio. You push one in, and the others pop out.

```jsx
import { useState } from 'react';

function SizeSelector() {
  const [size, setSize] = useState('medium');

  return (
    <div>
      <p>Choose your t-shirt size:</p>

      <label>
        <input
          type="radio"
          value="small"
          checked={size === 'small'}
          onChange={(event) => setSize(event.target.value)}
        />
        Small
      </label>
      <br />

      <label>
        <input
          type="radio"
          value="medium"
          checked={size === 'medium'}
          onChange={(event) => setSize(event.target.value)}
        />
        Medium
      </label>
      <br />

      <label>
        <input
          type="radio"
          value="large"
          checked={size === 'large'}
          onChange={(event) => setSize(event.target.value)}
        />
        Large
      </label>

      <p>You selected: {size}</p>
    </div>
  );
}

export default SizeSelector;
```

**What you will see:**

```
Choose your t-shirt size:

( ) Small
(●) Medium
( ) Large

You selected: medium
```

### How Radio Buttons Work

- All the radio buttons share the same state variable (`size`).
- Each radio button has a different `value` ("small", "medium", or "large").
- `checked={size === 'small'}` means this radio button is selected only when the state equals "small".
- When you click a radio button, `onChange` updates the state to that button's value. React re-renders, and only the matching radio button appears selected.

---

## Simple Form Validation

Form validation means checking if the user filled out the form correctly before accepting it. The simplest check is: did the user leave a field empty?

```jsx
import { useState } from 'react';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');

  function handleSubmit(event) {
    event.preventDefault();

    if (username.trim() === '') {
      setError('Username cannot be empty!');
      return;
    }

    setError('');
    alert('Welcome, ' + username + '!');
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>Username: </label>
      <input
        type="text"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
      />
      <button type="submit">Log In</button>

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
}

export default LoginForm;
```

**What you will see if you click Submit with an empty input:**

```
Username: [___________]  [Log In]
Username cannot be empty!
```

**What you will see if you type "Sara" and click Submit:**

```
A popup appears: "Welcome, Sara!"
```

### Line-by-Line Explanation of the Validation

```jsx
if (username.trim() === '') {
```

`trim()` removes any spaces from the beginning and end of the text. So if the user typed just spaces, `trim()` turns it into an empty string. We check if the result is an empty string (`''`).

```jsx
setError('Username cannot be empty!');
return;
```

If the username is empty, we set an error message in state. Then we `return`, which means "stop here, do not continue with the rest of the function."

```jsx
setError('');
```

If the username is valid, we clear any previous error message by setting it to an empty string.

```jsx
{error && <p style={{ color: 'red' }}>{error}</p>}
```

This only shows the error message paragraph when `error` is not an empty string. Remember, an empty string is falsy in JavaScript, so if `error` is `''`, the paragraph will not show up.

---

## Collecting Multiple Fields into One State Object

When your form has many fields, creating a separate `useState` for each one can get tiring. Instead, you can store all the form data in one object.

Think of it like a paper form. Instead of having separate sticky notes for each answer, you have one form sheet with all the answers on it.

```jsx
import { useState } from 'react';

function RegistrationForm() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
  });

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log('Form submitted:', formData);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>First Name: </label>
        <input
          type="text"
          name="firstName"
          value={formData.firstName}
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Last Name: </label>
        <input
          type="text"
          name="lastName"
          value={formData.lastName}
          onChange={handleChange}
        />
      </div>

      <div>
        <label>Email: </label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
        />
      </div>

      <button type="submit">Register</button>
    </form>
  );
}

export default RegistrationForm;
```

### The Key Parts Explained

```jsx
const [formData, setFormData] = useState({
  firstName: '',
  lastName: '',
  email: '',
});
```

Instead of three separate `useState` calls, we have one state that holds an object with three properties.

```jsx
const { name, value } = event.target;
```

This pulls out two things from the input element: its `name` attribute and its current `value`. This is called **destructuring**. It is a shortcut for writing:

```jsx
const name = event.target.name;
const value = event.target.value;
```

```jsx
setFormData({
  ...formData,
  [name]: value,
});
```

This is the important part. Let us break it down:

- `...formData` — This copies all the current form data. The three dots (`...`) are called the **spread operator**. Think of it like photocopying a form. You get a copy of everything.
- `[name]: value` — This updates just the one field that changed. The square brackets around `name` let us use a variable as the property name.

So if the user types in the "Email" field, this becomes:

```jsx
setFormData({
  ...formData,        // keep firstName and lastName as they are
  email: 'whatever the user typed',  // update only email
});
```

Each input has a `name` attribute that matches the property name in our state object. That is how React knows which field to update.

---

## Mini Project: Simple Contact Form

Let us build a complete contact form that collects a name, email, and message, validates the fields, and displays the submitted data.

```jsx
import { useState } from 'react';

function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });

  const [errors, setErrors] = useState({});
  const [submittedData, setSubmittedData] = useState(null);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  }

  function validate() {
    const newErrors = {};

    if (formData.name.trim() === '') {
      newErrors.name = 'Name is required.';
    }

    if (formData.email.trim() === '') {
      newErrors.email = 'Email is required.';
    }

    if (formData.message.trim() === '') {
      newErrors.message = 'Message is required.';
    }

    return newErrors;
  }

  function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate();

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setSubmittedData(null);
      return;
    }

    setErrors({});
    setSubmittedData(formData);
    setFormData({ name: '', email: '', message: '' });
  }

  return (
    <div>
      <h2>Contact Us</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Name: </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
          />
          {errors.name && <p style={{ color: 'red' }}>{errors.name}</p>}
        </div>

        <div>
          <label>Email: </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
          />
          {errors.email && <p style={{ color: 'red' }}>{errors.email}</p>}
        </div>

        <div>
          <label>Message: </label>
          <br />
          <textarea
            name="message"
            value={formData.message}
            onChange={handleChange}
            rows={4}
            cols={40}
          />
          {errors.message && <p style={{ color: 'red' }}>{errors.message}</p>}
        </div>

        <button type="submit">Send Message</button>
      </form>

      {submittedData && (
        <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
          <h3>Message Sent!</h3>
          <p><strong>Name:</strong> {submittedData.name}</p>
          <p><strong>Email:</strong> {submittedData.email}</p>
          <p><strong>Message:</strong> {submittedData.message}</p>
        </div>
      )}
    </div>
  );
}

export default ContactForm;
```

**What you will see if you submit with empty fields:**

```
Contact Us

Name: [___________]
Name is required.

Email: [___________]
Email is required.

Message:
+--------------------------------------+
|                                      |
+--------------------------------------+
Message is required.

[Send Message]
```

**What you will see after filling out and submitting the form:**

```
Contact Us

Name: [___________]
Email: [___________]
Message:
+--------------------------------------+
|                                      |
+--------------------------------------+
[Send Message]

Message Sent!
Name: Sara
Email: sara@email.com
Message: Hello, I love your website!
```

### How the Validation Works

```jsx
function validate() {
  const newErrors = {};

  if (formData.name.trim() === '') {
    newErrors.name = 'Name is required.';
  }
  // ... more checks ...

  return newErrors;
}
```

The `validate` function creates an empty object. For each field that is empty, it adds an error message to the object. If everything is filled in, the object stays empty.

```jsx
if (Object.keys(validationErrors).length > 0) {
```

`Object.keys()` gives us an array of all the property names in the object. If the array has any items (length is greater than 0), that means there are errors. We stop and show the errors. We do not submit the form.

After a successful submission, we clear the form by setting the form data back to empty strings and show the submitted data in a summary box.

---

## Quick Summary

| Concept | How It Works |
|---|---|
| Controlled component | React controls the input value through state |
| Text input | `value={state}` and `onChange={handler}` |
| Textarea | Same as text input, uses `value` attribute |
| Select dropdown | Same pattern, `value` on the `<select>` element |
| Checkbox | Uses `checked={state}` and `event.target.checked` |
| Radio buttons | Same `checked` pattern, shared state variable |
| Form submission | `onSubmit` on the form, `event.preventDefault()` inside |
| Validation | Check state values before accepting the submission |
| Multiple fields | Store all fields in one state object, use spread operator |

---

## Key Points to Remember

1. **In React, the state controls the input.** The input shows whatever is in the state. This is called a controlled component.

2. **Always use `event.preventDefault()`** in your form submission handler. Without it, the browser will refresh the page and your React app will lose its state.

3. **For checkboxes, use `checked` instead of `value`.** Read `event.target.checked` instead of `event.target.value`.

4. **The spread operator (`...`) copies an object.** When updating one field in a form object, spread the existing data first, then override the field that changed.

5. **Give each input a `name` attribute** that matches the property name in your state object. This lets you use one `handleChange` function for all inputs.

6. **Validation is just checking state values.** Before accepting a submission, check if the fields are empty or invalid.

---

## Practice Questions

1. What is a controlled component in React? Why do we call it "controlled"?

2. What does `event.preventDefault()` do, and why is it important in React forms?

3. How is handling a checkbox different from handling a text input? What attribute and property do we use instead of `value`?

4. If you have a form with five text fields, what are the two ways you can manage their state? Which one is better for many fields?

5. In the expression `setFormData({ ...formData, [name]: value })`, what does each part do?

---

## Exercises

### Exercise 1: Favorite Food Form

Create a form with:
- A text input for the user's favorite food
- A submit button
- After submission, show "Your favorite food is: [food]!" below the form
- If the input is empty, show an error message in red

### Exercise 2: Pizza Order Form

Create a form where the user can:
- Enter their name (text input)
- Choose a pizza size (radio buttons: Small, Medium, Large)
- Check a box for extra cheese (checkbox)
- Click "Place Order"
- After submission, show a summary: "Order for [name]: [size] pizza, extra cheese: yes/no"

### Exercise 3: Feedback Form

Create a feedback form with:
- A text input for the user's name
- A select dropdown to rate their experience (Excellent, Good, Average, Poor)
- A textarea for comments
- Validate that name and comments are not empty
- After submission, display all the feedback in a summary box and clear the form

---

## What Is Next?

You now know how to build forms in React. You can collect user input, validate it, and display it. Forms use `useState` to control their values, and you have seen how powerful that is.

In the next chapter, we will take a much deeper look at `useState`. You have been using it for simple strings and booleans, but state can hold arrays, objects, and more. We will learn how to update arrays and objects correctly, avoid common mistakes, and build a to-do list application. Get ready to level up your state skills.
