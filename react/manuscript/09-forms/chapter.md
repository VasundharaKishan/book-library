# Chapter 9: Forms — Controlled and Uncontrolled Components

---

## Learning Goals

By the end of this chapter, you will be able to:

- Explain the difference between controlled and uncontrolled components
- Build controlled forms with `useState` for all input types
- Handle text inputs, text areas, selects, checkboxes, radio buttons, and file inputs
- Manage complex form state with a single handler
- Validate forms on change, on blur, and on submit
- Show real-time validation feedback with clear error messages
- Build multi-step forms (form wizards)
- Use `useRef` with uncontrolled components
- Understand when to choose controlled vs uncontrolled
- Build production-quality forms with proper UX patterns

---

## Why Forms Are Special in React

Forms are one of the areas where React differs most from plain HTML. In a regular HTML page, the browser manages form state — it tracks what the user types, which checkboxes are checked, and which option is selected. When the form is submitted, the browser collects all the values and sends them to a server.

In React, you typically want **JavaScript to be in control** of the form data. This gives you the power to:

- Validate input in real time
- Enable or disable the submit button based on form validity
- Format input as the user types (e.g., phone numbers, credit cards)
- Submit form data via JavaScript (AJAX) without a page reload
- Conditionally show or hide fields based on other field values
- Share form values with other components

This leads to two fundamentally different approaches for handling form inputs in React: **controlled components** and **uncontrolled components**.

---

## Controlled Components

A **controlled component** is a form element whose value is controlled by React state. The input's value always reflects what is in state, and changes to the input update state.

The pattern has two parts:
1. **The `value` prop** — sets the input's value from state.
2. **The `onChange` handler** — updates state when the user types.

```jsx
import { useState } from "react";

function ControlledInput() {
  const [name, setName] = useState("");

  function handleChange(event) {
    setName(event.target.value);
  }

  return (
    <div>
      <label htmlFor="name">Name: </label>
      <input
        id="name"
        type="text"
        value={name}        // React state controls the display
        onChange={handleChange}  // User input updates state
      />
      <p>You typed: {name}</p>
    </div>
  );
}
```

**The data flow of a controlled input:**

```
User types "A"
    │
    ▼
onChange fires → event.target.value is "A"
    │
    ▼
setName("A") → state updates to "A"
    │
    ▼
Component re-renders → input's value prop is "A"
    │
    ▼
Input displays "A"
```

The input never manages its own value. React state is the **single source of truth**. If you do not update state in `onChange`, the input will not change — even if the user presses keys.

### Why Controlled Components?

This might seem like extra work compared to just letting the input manage itself. But having React control the value gives you complete power over the input:

```jsx
function UppercaseInput() {
  const [text, setText] = useState("");

  function handleChange(event) {
    // Transform the input as the user types
    setText(event.target.value.toUpperCase());
  }

  return (
    <input type="text" value={text} onChange={handleChange} />
  );
}
```

This would be difficult with an uncontrolled input. Because React controls the value, you can transform, validate, or restrict it before displaying it.

Other things you can do with controlled inputs:
- Limit character count
- Format as phone numbers or credit cards
- Prevent certain characters
- Reset the form programmatically
- Pre-fill values from an API

---

## Every Input Type as a Controlled Component

### Text Input

```jsx
const [username, setUsername] = useState("");

<input
  type="text"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
/>
```

### Email Input

```jsx
const [email, setEmail] = useState("");

<input
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

### Password Input

```jsx
const [password, setPassword] = useState("");

<input
  type="password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
/>
```

### Number Input

```jsx
const [age, setAge] = useState("");

<input
  type="number"
  value={age}
  onChange={(e) => setAge(e.target.value)}
  min="0"
  max="120"
/>
```

**Note:** Even with `type="number"`, `event.target.value` is always a string. Convert it when you need a number: `Number(e.target.value)` or `parseInt(e.target.value, 10)`.

### Text Area

In HTML, `<textarea>` uses children for its content: `<textarea>Default text</textarea>`. In React, `<textarea>` uses the `value` prop instead, making it consistent with `<input>`:

```jsx
const [bio, setBio] = useState("");

<textarea
  value={bio}
  onChange={(e) => setBio(e.target.value)}
  rows={4}
/>
```

### Select (Dropdown)

In HTML, you mark the selected option with a `selected` attribute. In React, you use the `value` prop on the `<select>` element:

```jsx
const [country, setCountry] = useState("");

<select value={country} onChange={(e) => setCountry(e.target.value)}>
  <option value="">Select a country</option>
  <option value="us">United States</option>
  <option value="uk">United Kingdom</option>
  <option value="ca">Canada</option>
  <option value="au">Australia</option>
</select>
```

**Why this is better:** In HTML, to change the selected option, you would need to find the old `<option>` and remove `selected`, then add `selected` to the new one. In React, you just change the state value, and React handles the rest.

### Multi-Select

```jsx
const [selectedFruits, setSelectedFruits] = useState([]);

function handleMultiSelect(event) {
  const options = event.target.options;
  const selected = [];
  for (let i = 0; i < options.length; i++) {
    if (options[i].selected) {
      selected.push(options[i].value);
    }
  }
  setSelectedFruits(selected);
}

<select multiple value={selectedFruits} onChange={handleMultiSelect} style={{ height: "120px" }}>
  <option value="apple">Apple</option>
  <option value="banana">Banana</option>
  <option value="cherry">Cherry</option>
  <option value="date">Date</option>
</select>
<p>Selected: {selectedFruits.join(", ") || "None"}</p>
```

### Checkbox (Single Boolean)

Checkboxes use `checked` instead of `value`, and `event.target.checked` instead of `event.target.value`:

```jsx
const [agreeToTerms, setAgreeToTerms] = useState(false);

<label>
  <input
    type="checkbox"
    checked={agreeToTerms}
    onChange={(e) => setAgreeToTerms(e.target.checked)}
  />
  I agree to the terms and conditions
</label>
```

### Checkbox Group (Multiple Selections)

When you have multiple checkboxes representing a set of choices:

```jsx
import { useState } from "react";

function HobbySelector() {
  const [hobbies, setHobbies] = useState([]);

  const allHobbies = ["Reading", "Gaming", "Cooking", "Hiking", "Photography", "Music"];

  function handleCheckboxChange(event) {
    const { value, checked } = event.target;

    if (checked) {
      // Add to array
      setHobbies((prev) => [...prev, value]);
    } else {
      // Remove from array
      setHobbies((prev) => prev.filter((hobby) => hobby !== value));
    }
  }

  return (
    <div>
      <h3>Select your hobbies:</h3>
      {allHobbies.map((hobby) => (
        <label key={hobby} style={{ display: "block", marginBottom: "0.5rem" }}>
          <input
            type="checkbox"
            value={hobby}
            checked={hobbies.includes(hobby)}
            onChange={handleCheckboxChange}
          />
          {hobby}
        </label>
      ))}
      <p>Selected: {hobbies.join(", ") || "None"}</p>
    </div>
  );
}
```

**How this works:**
- Each checkbox has a `value` (the hobby name) and `checked` (whether it is in the array).
- When checked, the hobby is added to the array with spread: `[...prev, value]`.
- When unchecked, the hobby is removed with filter: `prev.filter(h => h !== value)`.

### Radio Buttons

Radio buttons in a group share the same `name` and use `value` + `checked`:

```jsx
const [size, setSize] = useState("medium");

<div>
  <h3>Select size:</h3>
  {["small", "medium", "large", "extra-large"].map((option) => (
    <label key={option} style={{ display: "block", marginBottom: "0.25rem" }}>
      <input
        type="radio"
        name="size"
        value={option}
        checked={size === option}
        onChange={(e) => setSize(e.target.value)}
      />
      {option.charAt(0).toUpperCase() + option.slice(1)}
    </label>
  ))}
  <p>Selected: {size}</p>
</div>
```

**Key points for radio buttons:**
- All radios in a group must have the same `name`.
- `checked` is set by comparing the current state with the radio's `value`.
- Only one radio in a group can be checked at a time — React handles this automatically because only one value matches the state.

### Range (Slider)

```jsx
const [volume, setVolume] = useState(50);

<div>
  <label htmlFor="volume">Volume: {volume}%</label>
  <input
    id="volume"
    type="range"
    min="0"
    max="100"
    value={volume}
    onChange={(e) => setVolume(Number(e.target.value))}
  />
</div>
```

### Date Input

```jsx
const [date, setDate] = useState("");

<input
  type="date"
  value={date}
  onChange={(e) => setDate(e.target.value)}
/>
```

### Color Picker

```jsx
const [color, setColor] = useState("#3182ce");

<div>
  <input
    type="color"
    value={color}
    onChange={(e) => setColor(e.target.value)}
  />
  <span style={{ marginLeft: "0.5rem" }}>{color}</span>
</div>
```

---

## Managing Form State

### Individual useState Calls

For simple forms with a few fields:

```jsx
function SimpleForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    console.log({ name, email, message });
  }

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <textarea value={message} onChange={(e) => setMessage(e.target.value)} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

This works but becomes tedious with many fields — you get one `useState` call and one inline handler per field.

### Single State Object with One Handler

For larger forms, use a single state object and a unified handler. This is the recommended approach for most forms:

```jsx
import { useState } from "react";

function RegistrationForm() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    age: "",
    gender: "",
    newsletter: false,
    interests: [],
    bio: "",
  });

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function handleInterestChange(event) {
    const { value, checked } = event.target;

    setFormData((prev) => ({
      ...prev,
      interests: checked
        ? [...prev.interests, value]
        : prev.interests.filter((i) => i !== value),
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Form data:", formData);
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Registration</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="firstName">First Name:</label>
        <input
          id="firstName"
          name="firstName"
          type="text"
          value={formData.firstName}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="lastName">Last Name:</label>
        <input
          id="lastName"
          name="lastName"
          type="text"
          value={formData.lastName}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="confirmPassword">Confirm Password:</label>
        <input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={handleChange}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="age">Age:</label>
        <input
          id="age"
          name="age"
          type="number"
          value={formData.age}
          onChange={handleChange}
          min="13"
          max="120"
          style={{ width: "100px", padding: "0.5rem" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Gender:</label>
        <div style={{ display: "flex", gap: "1rem", marginTop: "0.25rem" }}>
          {["male", "female", "other", "prefer-not-to-say"].map((option) => (
            <label key={option}>
              <input
                type="radio"
                name="gender"
                value={option}
                checked={formData.gender === option}
                onChange={handleChange}
              />
              {option.split("-").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")}
            </label>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>Interests:</label>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "0.25rem" }}>
          {["Technology", "Sports", "Music", "Art", "Travel"].map((interest) => (
            <label key={interest}>
              <input
                type="checkbox"
                value={interest}
                checked={formData.interests.includes(interest)}
                onChange={handleInterestChange}
              />
              {interest}
            </label>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="bio">Bio:</label>
        <textarea
          id="bio"
          name="bio"
          value={formData.bio}
          onChange={handleChange}
          rows={4}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            name="newsletter"
            type="checkbox"
            checked={formData.newsletter}
            onChange={handleChange}
          />
          Subscribe to newsletter
        </label>
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem", fontSize: "1rem" }}>
        Register
      </button>
    </form>
  );
}
```

**How the unified handler works for different input types:**

```javascript
function handleChange(event) {
  const { name, value, type, checked } = event.target;

  setFormData((prev) => ({
    ...prev,                                    // Keep all other fields
    [name]: type === "checkbox" ? checked : value, // Update this one field
  }));
}
```

| Input Type | `name` | `type` | Value Used |
|-----------|--------|--------|------------|
| text | `"firstName"` | `"text"` | `event.target.value` |
| email | `"email"` | `"email"` | `event.target.value` |
| password | `"password"` | `"password"` | `event.target.value` |
| number | `"age"` | `"number"` | `event.target.value` (string) |
| radio | `"gender"` | `"radio"` | `event.target.value` |
| checkbox (single) | `"newsletter"` | `"checkbox"` | `event.target.checked` |
| textarea | `"bio"` | `"textarea"` | `event.target.value` |

**Why the checkbox group needs a separate handler:** The unified handler sets one field to one value. But checkbox groups need to add/remove items from an array — that is a different operation that cannot be handled with `[name]: value`.

### Resetting a Form

```jsx
const initialFormData = {
  firstName: "",
  lastName: "",
  email: "",
  // ... all fields with default values
};

function RegistrationForm() {
  const [formData, setFormData] = useState(initialFormData);

  function handleReset() {
    setFormData(initialFormData);
  }

  // ...
}
```

Define the initial state object outside the component (or use a function), then reset by calling `setFormData(initialFormData)`. This is much cleaner than clearing each field individually.

---

## Form Validation

Validation is the process of checking that form data meets certain rules before accepting it. There are three common strategies for when to validate:

### Strategy 1: Validate on Submit

Check all fields when the user clicks "Submit." This is the simplest approach:

```jsx
import { useState } from "react";

function ContactForm() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required.";
    } else if (formData.name.trim().length < 2) {
      newErrors.name = "Name must be at least 2 characters.";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address.";
    }

    if (!formData.message.trim()) {
      newErrors.message = "Message is required.";
    } else if (formData.message.trim().length < 10) {
      newErrors.message = "Message must be at least 10 characters.";
    }

    return newErrors;
  }

  function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate();
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length === 0) {
      console.log("Form is valid! Submitting:", formData);
      setIsSubmitted(true);
    }
  }

  if (isSubmitted) {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }}>
        <h2>Thank you, {formData.name}!</h2>
        <p>Your message has been sent.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Contact Us</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors.name ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {errors.name && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.name}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors.email ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {errors.email && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.email}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={4}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors.message ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
        />
        {errors.message && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.message}
          </p>
        )}
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem" }}>
        Send Message
      </button>
    </form>
  );
}
```

**The validation pattern:**

1. A `validate()` function checks each field and returns an errors object.
2. `handleSubmit` calls `validate()` and stores the result in `errors` state.
3. If the errors object is empty (`Object.keys(errors).length === 0`), the form is valid.
4. Error messages are conditionally rendered below each field.
5. Input borders turn red when there is an error.

### Strategy 2: Validate on Blur (When Field Loses Focus)

More user-friendly — validate each field when the user finishes with it:

```jsx
import { useState } from "react";

function BlurValidationForm() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // If field was already touched, validate on change too
    if (touched[name]) {
      validateField(name, value);
    }
  }

  function handleBlur(event) {
    const { name, value } = event.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    validateField(name, value);
  }

  function validateField(name, value) {
    let error = "";

    switch (name) {
      case "username":
        if (!value.trim()) {
          error = "Username is required.";
        } else if (value.length < 3) {
          error = "Username must be at least 3 characters.";
        } else if (value.length > 20) {
          error = "Username must be 20 characters or less.";
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
          error = "Username can only contain letters, numbers, and underscores.";
        }
        break;

      case "email":
        if (!value.trim()) {
          error = "Email is required.";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          error = "Please enter a valid email address.";
        }
        break;

      case "password":
        if (!value) {
          error = "Password is required.";
        } else if (value.length < 8) {
          error = "Password must be at least 8 characters.";
        } else if (!/[A-Z]/.test(value)) {
          error = "Password must contain at least one uppercase letter.";
        } else if (!/[0-9]/.test(value)) {
          error = "Password must contain at least one number.";
        }
        break;

      default:
        break;
    }

    setErrors((prev) => ({ ...prev, [name]: error }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    // Touch all fields to trigger validation display
    const allTouched = {};
    Object.keys(formData).forEach((key) => {
      allTouched[key] = true;
      validateField(key, formData[key]);
    });
    setTouched(allTouched);

    // Check if valid
    const hasErrors = Object.keys(formData).some((key) => {
      let error = "";
      // Re-validate to get current errors
      // (In a real app, you would consolidate this logic)
      if (key === "username" && (!formData[key].trim() || formData[key].length < 3)) error = "invalid";
      if (key === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData[key])) error = "invalid";
      if (key === "password" && formData[key].length < 8) error = "invalid";
      return error !== "";
    });

    if (!hasErrors) {
      console.log("Valid! Submitting:", formData);
    }
  }

  function getFieldStyle(name) {
    if (!touched[name]) return { border: "1px solid #e2e8f0" };
    if (errors[name]) return { border: "1px solid #e53e3e" };
    return { border: "1px solid #38a169" };
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Create Account</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="username">Username:</label>
        <input
          id="username"
          name="username"
          type="text"
          value={formData.username}
          onChange={handleChange}
          onBlur={handleBlur}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            borderRadius: "4px",
            ...getFieldStyle("username"),
          }}
        />
        {touched.username && errors.username && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.username}
          </p>
        )}
        {touched.username && !errors.username && formData.username && (
          <p style={{ color: "#38a169", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            Username is available.
          </p>
        )}
        <p style={{ color: "#a0aec0", fontSize: "0.75rem", margin: "0.25rem 0 0" }}>
          {formData.username.length}/20 characters
        </p>
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          onBlur={handleBlur}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            borderRadius: "4px",
            ...getFieldStyle("email"),
          }}
        />
        {touched.email && errors.email && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.email}
          </p>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="password">Password:</label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          onBlur={handleBlur}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            borderRadius: "4px",
            ...getFieldStyle("password"),
          }}
        />
        {touched.password && errors.password && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors.password}
          </p>
        )}
        {/* Password strength indicator */}
        {formData.password && (
          <PasswordStrength password={formData.password} />
        )}
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem", width: "100%" }}>
        Create Account
      </button>
    </form>
  );
}

function PasswordStrength({ password }) {
  function getStrength() {
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 1) return { label: "Weak", color: "#e53e3e", width: "20%" };
    if (score <= 2) return { label: "Fair", color: "#d69e2e", width: "40%" };
    if (score <= 3) return { label: "Good", color: "#38a169", width: "60%" };
    if (score <= 4) return { label: "Strong", color: "#2b6cb0", width: "80%" };
    return { label: "Very Strong", color: "#2f855a", width: "100%" };
  }

  const strength = getStrength();

  return (
    <div style={{ marginTop: "0.5rem" }}>
      <div style={{ backgroundColor: "#e2e8f0", borderRadius: "4px", height: "6px" }}>
        <div
          style={{
            backgroundColor: strength.color,
            height: "100%",
            borderRadius: "4px",
            width: strength.width,
            transition: "all 0.3s ease",
          }}
        />
      </div>
      <p style={{ color: strength.color, fontSize: "0.75rem", margin: "0.25rem 0 0" }}>
        {strength.label}
      </p>
    </div>
  );
}
```

**The blur validation pattern:**

1. A `touched` state object tracks which fields the user has interacted with.
2. `onBlur` marks the field as touched and validates it.
3. `onChange` only validates if the field is already touched (so errors appear after the first blur, then update in real time).
4. Error messages only show for touched fields.
5. Valid fields get a green border, invalid get red, untouched get gray.

### Strategy 3: Real-Time Validation (On Change)

Validate on every keystroke. Best for fields where instant feedback helps:

```jsx
function RealtimeEmailInput() {
  const [email, setEmail] = useState("");

  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const isEmpty = email.length === 0;

  return (
    <div>
      <label htmlFor="email">Email:</label>
      <div style={{ position: "relative" }}>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            width: "100%",
            padding: "0.5rem",
            paddingRight: "2rem",
            boxSizing: "border-box",
            border: `1px solid ${isEmpty ? "#e2e8f0" : isValid ? "#38a169" : "#e53e3e"}`,
            borderRadius: "4px",
          }}
        />
        {!isEmpty && (
          <span
            style={{
              position: "absolute",
              right: "0.5rem",
              top: "50%",
              transform: "translateY(-50%)",
              fontSize: "1.25rem",
            }}
          >
            {isValid ? "✓" : "✗"}
          </span>
        )}
      </div>
    </div>
  );
}
```

### Which Validation Strategy to Choose?

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  On Submit:   Simplest. Good for short forms.       │
│               User sees all errors at once.         │
│               Can be frustrating for long forms.    │
│                                                     │
│  On Blur:     Best user experience for most forms.  │
│               Validates as user moves through       │
│               fields. Does not interrupt typing.    │
│                                                     │
│  On Change:   Best for specific fields needing      │
│               instant feedback (password strength,  │
│               username availability). Can be noisy  │
│               if used for everything.               │
│                                                     │
│  Best practice: Combine blur + change.              │
│  First validation on blur, then update on change.   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Uncontrolled Components

An **uncontrolled component** lets the DOM handle the form data. Instead of tracking every change in React state, you read the value from the DOM when you need it — typically on form submission.

### Using useRef for Uncontrolled Inputs

```jsx
import { useRef } from "react";

function UncontrolledForm() {
  const nameRef = useRef(null);
  const emailRef = useRef(null);
  const messageRef = useRef(null);

  function handleSubmit(event) {
    event.preventDefault();

    const formData = {
      name: nameRef.current.value,
      email: emailRef.current.value,
      message: messageRef.current.value,
    };

    console.log("Form data:", formData);
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Contact Us (Uncontrolled)</h2>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="name">Name:</label>
        <input
          id="name"
          type="text"
          ref={nameRef}
          defaultValue=""
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="email">Email:</label>
        <input
          id="email"
          type="email"
          ref={emailRef}
          defaultValue=""
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="message">Message:</label>
        <textarea
          id="message"
          ref={messageRef}
          defaultValue=""
          rows={4}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem" }}>
        Send
      </button>
    </form>
  );
}
```

**Key differences from controlled components:**

| Controlled | Uncontrolled |
|-----------|-------------|
| `value={state}` | `defaultValue="..."` or no initial value |
| `onChange={handler}` | No `onChange` needed |
| State updates on every keystroke | Value read from DOM only when needed |
| React is the source of truth | DOM is the source of truth |
| Can transform/validate in real time | Validation only on submit |
| More code, more control | Less code, less control |

**`defaultValue` vs `value`:**
- `value` makes the input controlled — React controls it.
- `defaultValue` sets an initial value but lets the DOM manage changes afterward — the input is uncontrolled.

### File Inputs Are Always Uncontrolled

File inputs (`<input type="file">`) cannot be controlled in React because their value is read-only for security reasons. You must use `useRef`:

```jsx
import { useRef, useState } from "react";

function FileUpload() {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);

    // Create preview for images
    if (file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    } else {
      setPreview(null);
    }
  }

  function handleUpload() {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    console.log("Uploading:", {
      name: selectedFile.name,
      size: `${(selectedFile.size / 1024).toFixed(1)} KB`,
      type: selectedFile.type,
    });

    // In a real app, you would use FormData and fetch:
    // const formData = new FormData();
    // formData.append("file", selectedFile);
    // fetch("/api/upload", { method: "POST", body: formData });
  }

  function handleClear() {
    setSelectedFile(null);
    setPreview(null);
    fileInputRef.current.value = ""; // Reset the file input
  }

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Upload File</h2>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="image/*,.pdf,.doc,.docx"
        style={{ marginBottom: "1rem" }}
      />

      {selectedFile && (
        <div style={{
          padding: "1rem",
          backgroundColor: "#f7fafc",
          borderRadius: "8px",
          marginBottom: "1rem",
        }}>
          <p><strong>File:</strong> {selectedFile.name}</p>
          <p><strong>Size:</strong> {(selectedFile.size / 1024).toFixed(1)} KB</p>
          <p><strong>Type:</strong> {selectedFile.type}</p>

          {preview && (
            <img
              src={preview}
              alt="Preview"
              style={{ maxWidth: "100%", maxHeight: "200px", marginTop: "0.5rem", borderRadius: "4px" }}
            />
          )}

          <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
            <button onClick={handleUpload}>Upload</button>
            <button onClick={handleClear}>Clear</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

### When to Use Controlled vs Uncontrolled

```
Use CONTROLLED when:
├── You need real-time validation
├── You need to transform input (formatting, uppercase)
├── You need to conditionally enable/disable a submit button
├── You need to share form data with other components
├── The form has complex interdependent fields
└── You need to programmatically set values

Use UNCONTROLLED when:
├── The form is very simple (just submit and read values)
├── You are integrating with non-React code
├── You want less re-rendering (performance-sensitive)
├── You are working with file inputs (must be uncontrolled)
└── You are migrating an existing HTML form
```

**In practice, controlled components are the default choice for React applications.** Most React forms use controlled components because the benefits of having React control the data outweigh the extra code. Uncontrolled components are a valid alternative for simple cases.

---

## Dynamic Forms

### Conditional Fields

Show or hide fields based on other field values:

```jsx
import { useState } from "react";

function OrderForm() {
  const [formData, setFormData] = useState({
    orderType: "delivery",
    address: "",
    apartment: "",
    city: "",
    zipCode: "",
    pickupLocation: "",
    pickupTime: "",
    specialInstructions: "",
    needsGiftWrap: false,
    giftMessage: "",
  });

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Order:", formData);
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Place Order</h2>

      {/* Order type selection */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Order type:</label>
        <div style={{ display: "flex", gap: "1rem", marginTop: "0.25rem" }}>
          {["delivery", "pickup"].map((type) => (
            <label key={type}>
              <input
                type="radio"
                name="orderType"
                value={type}
                checked={formData.orderType === type}
                onChange={handleChange}
              />
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </label>
          ))}
        </div>
      </div>

      {/* Conditional delivery fields */}
      {formData.orderType === "delivery" && (
        <>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="address">Street Address:</label>
            <input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            />
          </div>
          <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ flex: 1 }}>
              <label htmlFor="city">City:</label>
              <input
                id="city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleChange}
                style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
              />
            </div>
            <div style={{ width: "120px" }}>
              <label htmlFor="zipCode">Zip Code:</label>
              <input
                id="zipCode"
                name="zipCode"
                type="text"
                value={formData.zipCode}
                onChange={handleChange}
                style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
              />
            </div>
          </div>
        </>
      )}

      {/* Conditional pickup fields */}
      {formData.orderType === "pickup" && (
        <>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="pickupLocation">Pickup Location:</label>
            <select
              id="pickupLocation"
              name="pickupLocation"
              value={formData.pickupLocation}
              onChange={handleChange}
              style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
            >
              <option value="">Select a location</option>
              <option value="downtown">Downtown Store</option>
              <option value="mall">Mall Location</option>
              <option value="airport">Airport Store</option>
            </select>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label htmlFor="pickupTime">Pickup Time:</label>
            <input
              id="pickupTime"
              name="pickupTime"
              type="time"
              value={formData.pickupTime}
              onChange={handleChange}
              style={{ padding: "0.5rem" }}
            />
          </div>
        </>
      )}

      {/* Gift wrap checkbox with conditional gift message */}
      <div style={{ marginBottom: "1rem" }}>
        <label>
          <input
            name="needsGiftWrap"
            type="checkbox"
            checked={formData.needsGiftWrap}
            onChange={handleChange}
          />
          Gift wrap this order
        </label>
      </div>

      {formData.needsGiftWrap && (
        <div style={{ marginBottom: "1rem" }}>
          <label htmlFor="giftMessage">Gift Message:</label>
          <textarea
            id="giftMessage"
            name="giftMessage"
            value={formData.giftMessage}
            onChange={handleChange}
            rows={3}
            placeholder="Write a message for the recipient..."
            style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
          />
        </div>
      )}

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="specialInstructions">Special Instructions:</label>
        <textarea
          id="specialInstructions"
          name="specialInstructions"
          value={formData.specialInstructions}
          onChange={handleChange}
          rows={2}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <button type="submit" style={{ padding: "0.75rem 1.5rem", width: "100%" }}>
        Place Order
      </button>
    </form>
  );
}
```

### Dynamic Field Lists (Add/Remove Fields)

Sometimes users need to add a variable number of inputs:

```jsx
import { useState } from "react";

function DynamicInputs() {
  const [fields, setFields] = useState([
    { id: 1, value: "" },
  ]);

  function handleFieldChange(id, newValue) {
    setFields((prev) =>
      prev.map((field) =>
        field.id === id ? { ...field, value: newValue } : field
      )
    );
  }

  function addField() {
    setFields((prev) => [
      ...prev,
      { id: Date.now(), value: "" },
    ]);
  }

  function removeField(id) {
    if (fields.length === 1) return; // Keep at least one field
    setFields((prev) => prev.filter((field) => field.id !== id));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const values = fields.map((f) => f.value).filter((v) => v.trim());
    console.log("Submitted values:", values);
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Skills</h2>
      <p style={{ color: "#718096", fontSize: "0.875rem" }}>
        Add your skills below.
      </p>

      {fields.map((field, index) => (
        <div
          key={field.id}
          style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", alignItems: "center" }}
        >
          <span style={{ color: "#a0aec0", width: "24px", textAlign: "right" }}>
            {index + 1}.
          </span>
          <input
            type="text"
            value={field.value}
            onChange={(e) => handleFieldChange(field.id, e.target.value)}
            placeholder={`Skill ${index + 1}`}
            style={{ flex: 1, padding: "0.5rem", border: "1px solid #e2e8f0", borderRadius: "4px" }}
          />
          <button
            type="button"
            onClick={() => removeField(field.id)}
            disabled={fields.length === 1}
            style={{
              padding: "0.5rem",
              backgroundColor: "transparent",
              border: "1px solid #e53e3e",
              color: fields.length === 1 ? "#cbd5e0" : "#e53e3e",
              borderRadius: "4px",
              cursor: fields.length === 1 ? "default" : "pointer",
            }}
          >
            Remove
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={addField}
        style={{
          padding: "0.5rem 1rem",
          backgroundColor: "transparent",
          border: "1px dashed #cbd5e0",
          borderRadius: "4px",
          cursor: "pointer",
          color: "#718096",
          width: "100%",
          marginBottom: "1rem",
        }}
      >
        + Add Skill
      </button>

      <button type="submit" style={{ padding: "0.75rem 1.5rem", width: "100%" }}>
        Save Skills
      </button>
    </form>
  );
}
```

**Key design decisions:**

1. Each field has a unique `id` (using `Date.now()` as a simple generator) — this is used as the `key` prop and to identify which field to update or remove.
2. The remove button is disabled when there is only one field — the user always has at least one input.
3. The "Add Skill" button uses `type="button"` — without this, it would trigger form submission because the default button type inside a form is `"submit"`.

---

## Multi-Step Forms (Form Wizard)

For long forms, splitting them into steps improves user experience:

```jsx
import { useState } from "react";

function MultiStepForm() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Personal Info
    firstName: "",
    lastName: "",
    email: "",
    // Step 2: Address
    address: "",
    city: "",
    state: "",
    zipCode: "",
    // Step 3: Preferences
    theme: "light",
    notifications: true,
    newsletter: false,
  });
  const [errors, setErrors] = useState({});

  const totalSteps = 3;

  function handleChange(event) {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  }

  function validateStep(currentStep) {
    const newErrors = {};

    if (currentStep === 1) {
      if (!formData.firstName.trim()) newErrors.firstName = "First name is required.";
      if (!formData.lastName.trim()) newErrors.lastName = "Last name is required.";
      if (!formData.email.trim()) {
        newErrors.email = "Email is required.";
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = "Invalid email address.";
      }
    }

    if (currentStep === 2) {
      if (!formData.address.trim()) newErrors.address = "Address is required.";
      if (!formData.city.trim()) newErrors.city = "City is required.";
      if (!formData.state.trim()) newErrors.state = "State is required.";
      if (!formData.zipCode.trim()) newErrors.zipCode = "Zip code is required.";
    }

    // Step 3 has no required fields

    return newErrors;
  }

  function handleNext() {
    const stepErrors = validateStep(step);
    setErrors(stepErrors);

    if (Object.keys(stepErrors).length === 0) {
      setStep((prev) => Math.min(prev + 1, totalSteps));
    }
  }

  function handleBack() {
    setStep((prev) => Math.max(prev - 1, 1));
  }

  function handleSubmit(event) {
    event.preventDefault();
    console.log("Final form data:", formData);
    alert("Form submitted successfully!");
  }

  function renderField(name, label, type = "text", extra = {}) {
    return (
      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor={name}>{label}:</label>
        <input
          id={name}
          name={name}
          type={type}
          value={formData[name]}
          onChange={handleChange}
          style={{
            width: "100%",
            padding: "0.5rem",
            boxSizing: "border-box",
            border: `1px solid ${errors[name] ? "#e53e3e" : "#e2e8f0"}`,
            borderRadius: "4px",
          }}
          {...extra}
        />
        {errors[name] && (
          <p style={{ color: "#e53e3e", fontSize: "0.875rem", margin: "0.25rem 0 0" }}>
            {errors[name]}
          </p>
        )}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Registration</h2>

      {/* Progress bar */}
      <div style={{ display: "flex", gap: "0.25rem", marginBottom: "2rem" }}>
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            style={{
              flex: 1,
              height: "4px",
              borderRadius: "2px",
              backgroundColor: s <= step ? "#3182ce" : "#e2e8f0",
              transition: "background-color 0.3s",
            }}
          />
        ))}
      </div>

      {/* Step indicators */}
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1.5rem" }}>
        {["Personal Info", "Address", "Preferences"].map((label, index) => (
          <div
            key={label}
            style={{
              textAlign: "center",
              color: index + 1 <= step ? "#3182ce" : "#a0aec0",
              fontSize: "0.875rem",
              fontWeight: index + 1 === step ? "bold" : "normal",
            }}
          >
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                border: `2px solid ${index + 1 <= step ? "#3182ce" : "#e2e8f0"}`,
                backgroundColor: index + 1 < step ? "#3182ce" : "white",
                color: index + 1 < step ? "white" : index + 1 === step ? "#3182ce" : "#a0aec0",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 0.25rem",
                fontSize: "0.75rem",
                fontWeight: "bold",
              }}
            >
              {index + 1 < step ? "✓" : index + 1}
            </div>
            {label}
          </div>
        ))}
      </div>

      {/* Step 1: Personal Info */}
      {step === 1 && (
        <div>
          <h3>Personal Information</h3>
          {renderField("firstName", "First Name")}
          {renderField("lastName", "Last Name")}
          {renderField("email", "Email", "email")}
        </div>
      )}

      {/* Step 2: Address */}
      {step === 2 && (
        <div>
          <h3>Address</h3>
          {renderField("address", "Street Address")}
          {renderField("city", "City")}
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>{renderField("state", "State")}</div>
            <div style={{ width: "140px" }}>{renderField("zipCode", "Zip Code")}</div>
          </div>
        </div>
      )}

      {/* Step 3: Preferences */}
      {step === 3 && (
        <div>
          <h3>Preferences</h3>
          <div style={{ marginBottom: "1rem" }}>
            <label>Theme:</label>
            <div style={{ display: "flex", gap: "1rem", marginTop: "0.25rem" }}>
              {["light", "dark", "auto"].map((option) => (
                <label key={option}>
                  <input
                    type="radio"
                    name="theme"
                    value={option}
                    checked={formData.theme === option}
                    onChange={handleChange}
                  />
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </label>
              ))}
            </div>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>
              <input
                name="notifications"
                type="checkbox"
                checked={formData.notifications}
                onChange={handleChange}
              />
              Enable push notifications
            </label>
          </div>
          <div style={{ marginBottom: "1rem" }}>
            <label>
              <input
                name="newsletter"
                type="checkbox"
                checked={formData.newsletter}
                onChange={handleChange}
              />
              Subscribe to newsletter
            </label>
          </div>

          {/* Summary */}
          <div style={{
            backgroundColor: "#f7fafc",
            padding: "1rem",
            borderRadius: "8px",
            marginTop: "1rem",
          }}>
            <h4 style={{ margin: "0 0 0.5rem" }}>Summary</h4>
            <p style={{ fontSize: "0.875rem", margin: "0.25rem 0" }}>
              <strong>Name:</strong> {formData.firstName} {formData.lastName}
            </p>
            <p style={{ fontSize: "0.875rem", margin: "0.25rem 0" }}>
              <strong>Email:</strong> {formData.email}
            </p>
            <p style={{ fontSize: "0.875rem", margin: "0.25rem 0" }}>
              <strong>Address:</strong> {formData.address}, {formData.city}, {formData.state} {formData.zipCode}
            </p>
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "1.5rem" }}>
        <button
          type="button"
          onClick={handleBack}
          disabled={step === 1}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: "transparent",
            border: "1px solid #e2e8f0",
            borderRadius: "4px",
            cursor: step === 1 ? "default" : "pointer",
            opacity: step === 1 ? 0.5 : 1,
          }}
        >
          Back
        </button>

        {step < totalSteps ? (
          <button
            type="button"
            onClick={handleNext}
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "#3182ce",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Next
          </button>
        ) : (
          <button
            type="submit"
            style={{
              padding: "0.75rem 1.5rem",
              backgroundColor: "#38a169",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Submit
          </button>
        )}
      </div>
    </form>
  );
}

export default MultiStepForm;
```

**Multi-step form design:**

1. **Single state, multiple steps.** All form data lives in one state object. Steps just control which fields are visible.
2. **Per-step validation.** Clicking "Next" validates only the current step's fields. This prevents overwhelming the user with errors for fields they have not seen yet.
3. **Progress indicator.** Shows completed, current, and upcoming steps.
4. **Summary on final step.** Before submission, the user sees all their data.
5. **Back navigation preserves data.** Going back does not lose what was entered.

---

## Form Submission Patterns

### Submitting to an API

```jsx
import { useState } from "react";

function ApiForm() {
  const [formData, setFormData] = useState({ title: "", body: "" });
  const [status, setStatus] = useState("idle"); // idle | submitting | success | error
  const [errorMessage, setErrorMessage] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("submitting");
    setErrorMessage("");

    try {
      const response = await fetch("https://jsonplaceholder.typicode.com/posts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();
      console.log("Created:", result);
      setStatus("success");
      setFormData({ title: "", body: "" }); // Reset form
    } catch (err) {
      setErrorMessage(err.message);
      setStatus("error");
    }
  }

  const isSubmitting = status === "submitting";

  if (status === "success") {
    return (
      <div style={{ textAlign: "center", padding: "2rem" }}>
        <h2 style={{ color: "#38a169" }}>Post Created!</h2>
        <p>Your post has been submitted successfully.</p>
        <button onClick={() => setStatus("idle")}>Create Another</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: "500px", margin: "0 auto" }}>
      <h2>Create Post</h2>

      {status === "error" && (
        <div style={{
          backgroundColor: "#fff5f5",
          border: "1px solid #fc8181",
          borderRadius: "4px",
          padding: "0.75rem",
          marginBottom: "1rem",
          color: "#e53e3e",
        }}>
          {errorMessage}
        </div>
      )}

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="title">Title:</label>
        <input
          id="title"
          name="title"
          type="text"
          value={formData.title}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="body">Body:</label>
        <textarea
          id="body"
          name="body"
          value={formData.body}
          onChange={handleChange}
          disabled={isSubmitting}
          required
          rows={6}
          style={{ width: "100%", padding: "0.5rem", boxSizing: "border-box" }}
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        style={{
          padding: "0.75rem 1.5rem",
          width: "100%",
          backgroundColor: isSubmitting ? "#a0aec0" : "#3182ce",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: isSubmitting ? "default" : "pointer",
        }}
      >
        {isSubmitting ? "Submitting..." : "Create Post"}
      </button>
    </form>
  );
}
```

**Submission UX best practices:**

1. **Disable the form while submitting** — prevents double submission.
2. **Change the button text** — "Submit" becomes "Submitting..." so the user knows something is happening.
3. **Show errors inline** — an error banner above the form.
4. **Reset on success** — clear the form and show a success message.
5. **Allow retry** — do not clear the form on error, so the user does not lose their input.

---

## Common Mistakes

1. **Mixing controlled and uncontrolled — the "changed from uncontrolled to controlled" warning.**

   ```jsx
   // ❌ Starting with undefined value then setting it
   const [name, setName] = useState(); // undefined!
   <input value={name} onChange={(e) => setName(e.target.value)} />
   // Warning: A component is changing an uncontrolled input to be controlled.

   // ✅ Always initialize with a defined value
   const [name, setName] = useState(""); // empty string
   ```

   When `value` is `undefined`, React treats the input as uncontrolled. When it changes to a string, React warns about the switch.

2. **Forgetting `event.preventDefault()` on form submission.**

   ```jsx
   // ❌ Page reloads
   function handleSubmit() {
     console.log("Submitted!");
   }

   // ✅ Prevent default first
   function handleSubmit(event) {
     event.preventDefault();
     console.log("Submitted!");
   }
   ```

3. **Using `event.target.value` for checkboxes.**

   ```jsx
   // ❌ value is always "on" for checkboxes
   onChange={(e) => setChecked(e.target.value)}

   // ✅ Use checked
   onChange={(e) => setChecked(e.target.checked)}
   ```

4. **Not using `type="button"` on non-submit buttons inside forms.**

   ```jsx
   // ❌ This triggers form submission!
   <button onClick={addItem}>Add Item</button>

   // ✅ Explicitly set type
   <button type="button" onClick={addItem}>Add Item</button>
   ```

5. **Not using `htmlFor` with labels.**

   ```jsx
   // ❌ Clicking the label does nothing
   <label>Name:</label>
   <input id="name" />

   // ✅ htmlFor connects label to input
   <label htmlFor="name">Name:</label>
   <input id="name" />
   ```

   When `htmlFor` matches an input's `id`, clicking the label focuses the input. This is important for accessibility and usability.

6. **Mutating state in checkbox group handlers.**

   ```jsx
   // ❌ Mutating the state array
   function handleCheck(value) {
     selected.push(value);        // NEVER push to state directly
     setSelected(selected);       // Same reference — React won't re-render
   }

   // ✅ Create a new array
   function handleCheck(value) {
     setSelected((prev) => [...prev, value]);
   }
   ```

---

## Best Practices

1. **Default to controlled components.** They give you full control over form data and enable real-time validation, formatting, and conditional logic.

2. **Use a single state object for forms with many fields** and a unified `handleChange` function with the `name` attribute.

3. **Validate on blur first, then on change after touch.** This gives the best user experience — not too aggressive, not too late.

4. **Show errors clearly** — red borders, text messages below the field, or icons. Never rely on `alert()` for validation feedback.

5. **Disable the submit button while submitting** and show a loading indicator. This prevents double submissions.

6. **Always use `event.preventDefault()`** in form submit handlers.

7. **Initialize all controlled inputs with defined values** (empty strings, `false`, etc.) — never `undefined` or `null`.

8. **Use `htmlFor` on every label** for accessibility.

9. **Use `type="button"` on non-submit buttons inside forms** to prevent accidental form submission.

10. **Keep validation logic in a separate function** that returns an errors object. This makes it testable and reusable.

---

## Summary

In this chapter, you learned:

- **Controlled components** have their value managed by React state. They use `value` + `onChange` and give you full control over the input.
- **Uncontrolled components** let the DOM manage the value. They use `defaultValue` and `useRef` to read values when needed.
- Every input type has a controlled pattern: text (`value`), checkbox (`checked`), radio (`checked` + shared `name`), select (`value` on the `<select>`), textarea (`value`), file (`ref` — always uncontrolled).
- A **unified `handleChange` function** with `event.target.name` can manage all form fields with a single state object.
- **Checkbox groups** need a separate handler that adds/removes values from an array.
- **Validation strategies**: on submit (simplest), on blur (best UX), on change (instant feedback). The best approach combines blur + change.
- The **`touched` pattern** tracks which fields the user has interacted with, preventing errors from appearing before the user has had a chance to fill in a field.
- **Dynamic forms** can show/hide fields conditionally and allow users to add/remove fields.
- **Multi-step forms** split long forms into manageable steps with per-step validation and progress indicators.
- **Form submission** should disable the form, show loading state, handle errors without clearing the form, and show a success state.

---

## Interview Questions

**Q1: What is the difference between controlled and uncontrolled components in React?**

A controlled component has its value managed by React state — the input's `value` prop is set from state, and an `onChange` handler updates state on every change. React is the single source of truth. An uncontrolled component lets the DOM manage the value — you set a `defaultValue` and read the value from the DOM (via a ref) when needed. Controlled components offer more control (real-time validation, formatting, conditional logic) and are the standard choice in React. Uncontrolled components are simpler but offer less flexibility.

**Q2: Why do you need to initialize controlled input state with an empty string instead of undefined?**

If a controlled input's `value` prop starts as `undefined`, React treats it as uncontrolled — the DOM manages the value. When state later becomes a string (e.g., after the user types), React warns: "A component is changing an uncontrolled input to be controlled." This is because React determines whether an input is controlled at mount time based on whether `value` is defined. Initializing with `""` (empty string) ensures the input is controlled from the start.

**Q3: How do you handle multiple form inputs with a single onChange handler?**

Give each input a `name` attribute that matches the corresponding key in your state object. In the handler, use `event.target.name` to identify which field changed, `event.target.value` for the new value (or `event.target.checked` for checkboxes), and computed property names to update the right field: `setFormData(prev => ({ ...prev, [name]: value }))`.

**Q4: What is the difference between the `value` and `defaultValue` props?**

`value` makes the input controlled — React sets and maintains the displayed value. Without an `onChange` handler, the input becomes read-only. `defaultValue` sets the initial value but lets the DOM manage subsequent changes — the input is uncontrolled. Use `value` for controlled components (most forms) and `defaultValue` for uncontrolled components or when integrating with non-React code.

**Q5: How do you handle checkbox groups (multiple checkboxes for the same field)?**

Store the selected values as an array in state. When a checkbox is toggled, check `event.target.checked`: if true, add the value to the array (`[...prev, value]`); if false, remove it (`prev.filter(v => v !== value)`). Set each checkbox's `checked` prop by checking if the array includes that value (`checked={selectedItems.includes(item)}`). This requires a separate handler from the unified text input handler because it needs to add/remove from an array.

**Q6: What are the different form validation strategies, and when would you use each?**

On-submit validation checks all fields when the form is submitted — simplest to implement, good for short forms. On-blur validation checks each field when it loses focus — best general UX because it gives feedback after the user finishes a field without interrupting typing. On-change validation checks on every keystroke — best for specific fields needing instant feedback (password strength, character counts). The recommended approach combines blur and change: validate first when the field loses focus, then re-validate on change after it has been touched.

**Q7: Why is `type="button"` important for non-submit buttons inside a form?**

The default `type` for a `<button>` element is `"submit"`. Inside a `<form>`, clicking any button without an explicit `type` triggers form submission (including page reload if `preventDefault` is not called on the form's submit handler). Buttons that should not submit the form — like "Add Item," "Remove," or "Clear" — must have `type="button"` to prevent this default behavior.

**Q8: How do you implement a multi-step form in React?**

Use a single state object for all form data across all steps, and a `step` state variable to track the current step. Render different form fields based on the current step using conditional rendering. Validate only the current step's fields before advancing to the next step. Navigation buttons (Back/Next/Submit) control the step state. The final step can show a summary of all data and a submit button. All data persists across steps because it lives in a single state object that is not cleared when moving between steps.

---

## Practice Exercises

**Exercise 1: Comprehensive Registration Form**

Build a registration form with:
- First name, last name, email, phone, password, confirm password
- Date of birth (date input)
- Country (select dropdown with at least 10 countries)
- Gender (radio buttons)
- Interests (checkbox group with at least 6 options)
- Bio (textarea with character count, max 500)
- Profile visibility (radio: public, private, friends-only)
- All fields validated on blur with appropriate rules
- Password strength meter
- Submit button disabled until all required fields are valid
- Success message after submission

**Exercise 2: Dynamic Invoice Form**

Create an invoice form where:
- The user enters client name and email at the top
- Below that, they can add line items (description, quantity, unit price)
- Each line item shows its subtotal (quantity × price)
- The user can add and remove line items
- The form shows a running total at the bottom
- Include a tax rate input that affects the total
- Validate that all line items have a description and positive quantity/price
- Show the grand total (subtotal + tax)

**Exercise 3: Settings Form with Sections**

Build a settings page with:
- Multiple sections: Profile, Notifications, Privacy, Appearance
- Each section is collapsible (accordion style)
- Profile: name, email, bio, avatar URL
- Notifications: email notifications (checkbox), push notifications (checkbox), notification frequency (select)
- Privacy: profile visibility (radio), show email (checkbox), allow messages from strangers (checkbox)
- Appearance: theme (radio: light/dark/auto), font size (range slider), compact mode (checkbox)
- A "Save Changes" button that only enables when something has changed
- A "Reset to Defaults" button
- Show which sections have unsaved changes

**Exercise 4: File Upload with Drag and Drop**

Create a file upload component with:
- A file input button
- A drag-and-drop zone that highlights when a file is dragged over
- File type validation (only accept images and PDFs)
- File size validation (max 5MB)
- Preview for images, icon for PDFs
- Multiple file upload support
- A list of uploaded files with individual remove buttons
- Upload progress simulation

**Exercise 5: Address Form with Autocomplete**

Build an address form that:
- Has fields for street, city, state, zip code, country
- When the user selects a country, the state/province field shows relevant options
- When the user enters a zip code, auto-fill city and state (simulate with a lookup object)
- Validate the format of the zip code based on the selected country
- Show the formatted address as a preview below the form

---

## What Is Next?

You now have complete mastery of forms in React — from simple text inputs to complex multi-step wizards with real-time validation. Forms are one of the most common UI patterns, and these skills will be used in almost every React application you build.

In Chapter 10, we will explore **useRef and DOM Manipulation** — learning how to interact with DOM elements directly, manage focus, create uncontrolled components, and store mutable values that persist across renders without causing re-renders.
