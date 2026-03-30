# Chapter 24: Final Mini Project -- Weather App

This is it. The final chapter. Everything you have learned in this book comes together here. We are going to build a real weather app from scratch. You will type in a city name, and the app will show you the current weather for that city.

This project uses components, state, effects, API calls, loading states, error handling, and styling. By the end of this chapter, you will have a working app that you can show to friends, family, or even put on your portfolio.

Let us get started.

---

## What You Will Learn

- How to plan a React project before writing code
- How to get a free API key from OpenWeatherMap
- How to build multiple components that work together
- How to fetch real weather data from an API
- How to handle loading and error states
- How to add simple CSS styling
- How to add a Celsius/Fahrenheit toggle

## Why This Chapter Matters

Building a complete project is the best way to solidify your learning. Reading about React is like reading about swimming. You understand the theory, but you need to jump in the water. This project is your pool.

---

## What We Will Build

Our weather app will have these features:

1. A search bar where the user can type a city name
2. A button to search for the weather
3. A card that shows the city name, temperature, weather description, and an icon
4. A loading message while data is being fetched
5. An error message if something goes wrong (like an invalid city name)
6. A button to switch between Celsius and Fahrenheit

### The Components We Will Create

| Component | Purpose |
|-----------|---------|
| `App` | The main component that holds everything together |
| `SearchBar` | The input field and search button |
| `WeatherCard` | Shows the weather data |
| `ErrorMessage` | Shows error messages |
| `LoadingSpinner` | Shows a loading message |

---

## Getting a Free API Key from OpenWeatherMap

Before we write any code, we need a way to get weather data. We will use a free service called OpenWeatherMap. An API (Application Programming Interface) is a way for your app to ask another service for data.

### How to Get Your Free API Key

1. Go to [https://openweathermap.org](https://openweathermap.org) in your browser.
2. Click "Sign Up" and create a free account.
3. After signing up and verifying your email, go to your account page.
4. Look for a section called "API keys."
5. You will see a key that looks like a long string of letters and numbers, like `abc123def456ghi789`.
6. Copy this key. You will need it soon.

**Important:** Your API key is private. Do not share it publicly. It is free, but it is connected to your account.

**Note:** New API keys can take up to 2 hours to become active. If your first attempt does not work, wait a bit and try again.

---

## Step 1: Set Up the Project

Open your terminal and create a new React project.

```bash
npx create-react-app weather-app
cd weather-app
```

This creates a new folder called `weather-app` with all the files you need.

Now start the development server to make sure everything works.

```bash
npm start
```

Your browser should open and show the default React page. Great. We are ready to build.

### Clean Up the Default Files

Open the `src` folder. You will see several files. We only need a few of them. Open `App.js` and replace everything inside with this:

```jsx
function App() {
  return (
    <div className="app">
      <h1>Weather App</h1>
    </div>
  );
}

export default App;
```

Open `App.css` and delete everything inside it. We will add our own styles later.

Open `index.css` and replace everything with this basic reset:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f0f4f8;
  color: #333;
}
```

### Line-by-Line Explanation of index.css

- `*` selects every element on the page.
- `margin: 0` and `padding: 0` remove the default spacing that browsers add.
- `box-sizing: border-box` makes width and height calculations easier. It includes padding and borders in the total size.
- `font-family: Arial, sans-serif` sets the text font for the entire page.
- `background-color: #f0f4f8` gives the page a light gray-blue background.
- `color: #333` makes the text dark gray (easier on the eyes than pure black).

---

## Step 2: Create the SearchBar Component

Create a new file at `src/SearchBar.js`.

```jsx
import { useState } from "react";

function SearchBar({ onSearch }) {
  const [city, setCity] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (city.trim() === "") {
      return;
    }

    onSearch(city);
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter city name..."
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;
```

### Line-by-Line Explanation

- `import { useState } from "react"` -- We need `useState` to track what the user types.
- `function SearchBar({ onSearch })` -- This component receives a function called `onSearch` from its parent. We destructure it from props.
- `const [city, setCity] = useState("")` -- We create a state variable called `city` that starts as an empty string.
- `function handleSubmit(event)` -- This function runs when the user submits the form (clicks the button or presses Enter).
- `event.preventDefault()` -- By default, a form submission refreshes the entire page. This line stops that from happening.
- `if (city.trim() === "")` -- `trim()` removes spaces from both ends of the text. If the user typed only spaces, we do nothing.
- `onSearch(city)` -- We call the function that the parent gave us, passing the city name up.
- `value={city}` -- This makes the input a "controlled component." React controls what the input shows.
- `onChange={(e) => setCity(e.target.value)}` -- When the user types, we update the `city` state with whatever they typed.

### Expected Behavior

The user types a city name. When they click "Search" or press Enter, the `onSearch` function is called with the city name. The search bar itself does not fetch data. It just tells the parent what city to search for.

---

## Step 3: Fetch Weather Data from the API

Now let us update `App.js` to use the `SearchBar` and fetch weather data.

```jsx
import { useState } from "react";
import SearchBar from "./SearchBar";

const API_KEY = "YOUR_API_KEY_HERE";
const API_URL = "https://api.openweathermap.org/data/2.5/weather";

function App() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleSearch(city) {
    setLoading(true);
    setError(null);
    setWeather(null);

    fetch(`${API_URL}?q=${city}&appid=${API_KEY}&units=metric`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("City not found");
        }
        return response.json();
      })
      .then((data) => {
        setWeather(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  return (
    <div className="app">
      <h1>Weather App</h1>
      <SearchBar onSearch={handleSearch} />

      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {weather && <p>Temperature: {weather.main.temp} C</p>}
    </div>
  );
}

export default App;
```

**Important:** Replace `YOUR_API_KEY_HERE` with the API key you got from OpenWeatherMap.

### Line-by-Line Explanation

- `const API_KEY = "YOUR_API_KEY_HERE"` -- A constant that stores your API key. Using a constant makes it easy to find and change.
- `const API_URL = "..."` -- The base URL for the OpenWeatherMap API.
- `const [weather, setWeather] = useState(null)` -- Stores the weather data. Starts as `null` because we have no data yet.
- `const [loading, setLoading] = useState(false)` -- Tracks whether we are waiting for data.
- `const [error, setError] = useState(null)` -- Stores any error message.
- `setLoading(true)` -- When a search starts, we set loading to true.
- `setError(null)` -- Clear any previous error.
- `setWeather(null)` -- Clear any previous weather data.
- `` fetch(`${API_URL}?q=${city}&appid=${API_KEY}&units=metric`) `` -- This sends a request to the weather API. `q=${city}` tells it which city. `units=metric` gives us temperatures in Celsius.
- `if (!response.ok)` -- If the response is not OK (like a 404 error for a city that does not exist), we throw an error.
- `throw new Error("City not found")` -- Creates an error that will be caught by the `.catch()` block.
- `.catch((err) => {...})` -- If anything goes wrong, we save the error message and stop loading.
- `{loading && <p>Loading...</p>}` -- Show "Loading..." only when `loading` is true.
- `{error && <p>{error}</p>}` -- Show the error only when there is one.
- `{weather && <p>...</p>}` -- Show the temperature only when we have weather data.

### Expected Output

When you type "London" and click Search, you should see something like:

```
Temperature: 15.2 C
```

If you type a city that does not exist (like "Xyzabc"), you should see:

```
City not found
```

---

## Step 4: Display the Weather Data in a WeatherCard

Let us create a proper component to show the weather data. Create a new file at `src/WeatherCard.js`.

```jsx
function WeatherCard({ weather, unit }) {
  const temperature = unit === "celsius"
    ? Math.round(weather.main.temp)
    : Math.round(weather.main.temp * 9 / 5 + 32);

  const unitSymbol = unit === "celsius" ? "C" : "F";

  const iconCode = weather.weather[0].icon;
  const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

  return (
    <div className="weather-card">
      <h2>{weather.name}, {weather.sys.country}</h2>
      <img src={iconUrl} alt={weather.weather[0].description} />
      <p className="temperature">
        {temperature}&deg;{unitSymbol}
      </p>
      <p className="description">{weather.weather[0].description}</p>
      <div className="details">
        <p>Humidity: {weather.main.humidity}%</p>
        <p>Wind: {weather.wind.speed} m/s</p>
      </div>
    </div>
  );
}

export default WeatherCard;
```

### Line-by-Line Explanation

- `function WeatherCard({ weather, unit })` -- This component receives the weather data and the current temperature unit (Celsius or Fahrenheit).
- `const temperature = unit === "celsius" ? ... : ...` -- If the unit is Celsius, we use the temperature as is. If it is Fahrenheit, we convert it using the formula: `(Celsius * 9/5) + 32`.
- `Math.round(...)` -- Rounds the number to the nearest whole number. Nobody needs to see `15.237` degrees.
- `const unitSymbol` -- Shows "C" or "F" depending on the selected unit.
- `const iconCode = weather.weather[0].icon` -- The API gives us a code for a weather icon (like "01d" for sunny).
- `const iconUrl = ...` -- OpenWeatherMap provides free weather icons at this URL pattern.
- `&deg;` -- This is an HTML code that shows the degree symbol (the little circle: 15°C).
- `weather.name` -- The city name from the API.
- `weather.sys.country` -- The country code (like "GB" for Great Britain).
- `weather.weather[0].description` -- A text description like "clear sky" or "light rain."
- `weather.main.humidity` -- The humidity percentage.
- `weather.wind.speed` -- The wind speed in meters per second.

---

## Step 5: Handle Loading and Error States

Let us create proper components for loading and error states.

### Create `src/LoadingSpinner.js`

```jsx
function LoadingSpinner() {
  return (
    <div className="loading">
      <p>Loading weather data...</p>
    </div>
  );
}

export default LoadingSpinner;
```

### Create `src/ErrorMessage.js`

```jsx
function ErrorMessage({ message }) {
  return (
    <div className="error-message">
      <p>Oops! {message}</p>
      <p>Please check the city name and try again.</p>
    </div>
  );
}

export default ErrorMessage;
```

### Update `App.js` to Use These Components

```jsx
import { useState } from "react";
import SearchBar from "./SearchBar";
import WeatherCard from "./WeatherCard";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";

const API_KEY = "YOUR_API_KEY_HERE";
const API_URL = "https://api.openweathermap.org/data/2.5/weather";

function App() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [unit, setUnit] = useState("celsius");

  function handleSearch(city) {
    setLoading(true);
    setError(null);
    setWeather(null);

    fetch(`${API_URL}?q=${city}&appid=${API_KEY}&units=metric`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("City not found");
        }
        return response.json();
      })
      .then((data) => {
        setWeather(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  function toggleUnit() {
    setUnit(unit === "celsius" ? "fahrenheit" : "celsius");
  }

  return (
    <div className="app">
      <h1>Weather App</h1>
      <SearchBar onSearch={handleSearch} />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {weather && (
        <>
          <WeatherCard weather={weather} unit={unit} />
          <button className="unit-toggle" onClick={toggleUnit}>
            Show in {unit === "celsius" ? "Fahrenheit" : "Celsius"}
          </button>
        </>
      )}
    </div>
  );
}

export default App;
```

### What Changed

- We imported `WeatherCard`, `LoadingSpinner`, and `ErrorMessage`.
- We added a `unit` state that tracks whether to show Celsius or Fahrenheit.
- We added a `toggleUnit` function that switches between the two units.
- We replaced the simple `<p>` tags with our proper components.
- We added a toggle button that only appears when weather data is available.

---

## Step 6: Add Simple CSS Styling

Open `src/App.css` and add these styles:

```css
.app {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}

.app h1 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 28px;
}

/* Search Bar */
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
}

.search-bar input:focus {
  border-color: #3498db;
}

.search-bar button {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.search-bar button:hover {
  background-color: #2980b9;
}

/* Weather Card */
.weather-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.weather-card h2 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.weather-card img {
  width: 100px;
  height: 100px;
}

.weather-card .temperature {
  font-size: 48px;
  font-weight: bold;
  color: #e74c3c;
  margin: 5px 0;
}

.weather-card .description {
  font-size: 18px;
  color: #7f8c8d;
  text-transform: capitalize;
  margin-bottom: 15px;
}

.weather-card .details {
  display: flex;
  justify-content: center;
  gap: 30px;
  color: #555;
}

/* Unit Toggle */
.unit-toggle {
  padding: 8px 20px;
  font-size: 14px;
  background-color: #ecf0f1;
  border: 2px solid #bdc3c7;
  border-radius: 8px;
  cursor: pointer;
  color: #333;
}

.unit-toggle:hover {
  background-color: #bdc3c7;
}

/* Loading */
.loading {
  margin: 30px 0;
  color: #3498db;
  font-size: 18px;
}

/* Error */
.error-message {
  background-color: #fee;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  color: #c0392b;
}
```

Now import the CSS in `App.js`. Add this line at the top of `App.js`:

```jsx
import "./App.css";
```

### CSS Explanation for Key Parts

- `max-width: 500px` and `margin: 50px auto` -- Centers the app and limits its width.
- `display: flex` on the search bar -- Places the input and button side by side.
- `gap: 10px` -- Adds space between the input and the button.
- `flex: 1` on the input -- Makes the input take up all remaining space.
- `border-radius: 8px` -- Rounds the corners of elements.
- `box-shadow` -- Adds a subtle shadow under the weather card to make it look like it floats.
- `text-transform: capitalize` -- Makes the first letter of the weather description uppercase.
- `cursor: pointer` -- Changes the mouse cursor to a hand when hovering over buttons.

---

## Step 7: Final Touches

Let us finalize our `App.js` with the import for styles included and everything polished.

### Complete Final Code

Here is every file in the project, complete and ready to use.

### `src/index.js`

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

This is the entry point. It renders the `App` component inside the HTML page.

### `src/index.css`

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f0f4f8;
  color: #333;
  min-height: 100vh;
}
```

### `src/App.js`

```jsx
import { useState } from "react";
import SearchBar from "./SearchBar";
import WeatherCard from "./WeatherCard";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";
import "./App.css";

const API_KEY = "YOUR_API_KEY_HERE";
const API_URL = "https://api.openweathermap.org/data/2.5/weather";

function App() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [unit, setUnit] = useState("celsius");

  function handleSearch(city) {
    setLoading(true);
    setError(null);
    setWeather(null);

    fetch(`${API_URL}?q=${city}&appid=${API_KEY}&units=metric`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("City not found");
        }
        return response.json();
      })
      .then((data) => {
        setWeather(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }

  function toggleUnit() {
    setUnit(unit === "celsius" ? "fahrenheit" : "celsius");
  }

  return (
    <div className="app">
      <h1>Weather App</h1>
      <SearchBar onSearch={handleSearch} />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {weather && (
        <>
          <WeatherCard weather={weather} unit={unit} />
          <button className="unit-toggle" onClick={toggleUnit}>
            Show in {unit === "celsius" ? "Fahrenheit" : "Celsius"}
          </button>
        </>
      )}
    </div>
  );
}

export default App;
```

### `src/SearchBar.js`

```jsx
import { useState } from "react";

function SearchBar({ onSearch }) {
  const [city, setCity] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    if (city.trim() === "") {
      return;
    }

    onSearch(city);
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter city name..."
        value={city}
        onChange={(e) => setCity(e.target.value)}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;
```

### `src/WeatherCard.js`

```jsx
function WeatherCard({ weather, unit }) {
  const temperature = unit === "celsius"
    ? Math.round(weather.main.temp)
    : Math.round(weather.main.temp * 9 / 5 + 32);

  const unitSymbol = unit === "celsius" ? "C" : "F";

  const iconCode = weather.weather[0].icon;
  const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

  return (
    <div className="weather-card">
      <h2>{weather.name}, {weather.sys.country}</h2>
      <img src={iconUrl} alt={weather.weather[0].description} />
      <p className="temperature">
        {temperature}&deg;{unitSymbol}
      </p>
      <p className="description">{weather.weather[0].description}</p>
      <div className="details">
        <p>Humidity: {weather.main.humidity}%</p>
        <p>Wind: {weather.wind.speed} m/s</p>
      </div>
    </div>
  );
}

export default WeatherCard;
```

### `src/LoadingSpinner.js`

```jsx
function LoadingSpinner() {
  return (
    <div className="loading">
      <p>Loading weather data...</p>
    </div>
  );
}

export default LoadingSpinner;
```

### `src/ErrorMessage.js`

```jsx
function ErrorMessage({ message }) {
  return (
    <div className="error-message">
      <p>Oops! {message}</p>
      <p>Please check the city name and try again.</p>
    </div>
  );
}

export default ErrorMessage;
```

### `src/App.css`

```css
.app {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
  text-align: center;
}

.app h1 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 28px;
}

/* Search Bar */
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-bar input {
  flex: 1;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
}

.search-bar input:focus {
  border-color: #3498db;
}

.search-bar button {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.search-bar button:hover {
  background-color: #2980b9;
}

/* Weather Card */
.weather-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.weather-card h2 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.weather-card img {
  width: 100px;
  height: 100px;
}

.weather-card .temperature {
  font-size: 48px;
  font-weight: bold;
  color: #e74c3c;
  margin: 5px 0;
}

.weather-card .description {
  font-size: 18px;
  color: #7f8c8d;
  text-transform: capitalize;
  margin-bottom: 15px;
}

.weather-card .details {
  display: flex;
  justify-content: center;
  gap: 30px;
  color: #555;
}

/* Unit Toggle */
.unit-toggle {
  padding: 8px 20px;
  font-size: 14px;
  background-color: #ecf0f1;
  border: 2px solid #bdc3c7;
  border-radius: 8px;
  cursor: pointer;
  color: #333;
}

.unit-toggle:hover {
  background-color: #bdc3c7;
}

/* Loading */
.loading {
  margin: 30px 0;
  color: #3498db;
  font-size: 18px;
}

/* Error */
.error-message {
  background-color: #fee;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  color: #c0392b;
}
```

---

## How the App Works: A Complete Walkthrough

Here is what happens when a user searches for a city:

1. The user types "Tokyo" into the search bar and clicks "Search."
2. The `SearchBar` component calls `onSearch("Tokyo")`.
3. The `App` component receives this and calls `handleSearch("Tokyo")`.
4. `handleSearch` sets `loading` to `true`, clears any previous error and weather data.
5. React re-renders. The `LoadingSpinner` appears because `loading` is `true`.
6. `fetch` sends a request to the OpenWeatherMap API.
7. The API sends back weather data for Tokyo.
8. `handleSearch` saves the data in `weather` state and sets `loading` to `false`.
9. React re-renders. The `LoadingSpinner` disappears. The `WeatherCard` appears with the weather data.
10. The user clicks "Show in Fahrenheit."
11. `toggleUnit` changes `unit` from `"celsius"` to `"fahrenheit"`.
12. React re-renders. `WeatherCard` recalculates the temperature and shows it in Fahrenheit.

If the user types a city that does not exist:

1. The API sends back an error response.
2. `response.ok` is `false`, so we throw an error.
3. The `.catch` block saves the error message and sets `loading` to `false`.
4. React re-renders. The `ErrorMessage` component appears.

---

## Quick Summary

| Step | What We Did |
|------|-------------|
| 1 | Set up the project and cleaned up default files |
| 2 | Created the SearchBar component with a controlled input |
| 3 | Added data fetching with fetch, loading, and error handling |
| 4 | Created the WeatherCard component to display weather data |
| 5 | Created LoadingSpinner and ErrorMessage components |
| 6 | Added CSS styling for a clean, modern look |
| 7 | Added the Celsius/Fahrenheit toggle and finalized all code |

---

## Key Points to Remember

1. **Plan before you code.** Decide what components you need and what each one does.
2. **Handle all three states:** loading, error, and success. Real apps must deal with all of them.
3. **Keep components focused.** Each component has one job.
4. **Use constants for API URLs and keys.** Do not scatter them throughout your code.
5. **Test as you go.** After each step, make sure your app works before moving on.

---

## Congratulations!

You did it. You built a complete, working React application from scratch.

Take a moment to appreciate what you have accomplished. At the beginning of this book, you might not have known what a component was. Now you have built an app with multiple components, state management, API calls, error handling, and styling. That is a real achievement.

### What You Have Learned in This Book

- What React is and why it is useful
- How to create components
- How to use JSX
- How to manage state with `useState`
- How to handle side effects with `useEffect`
- How to pass data with props
- How to handle user events
- How to render lists and use keys
- How to do conditional rendering
- How to fetch data from APIs
- How to handle forms
- How to use React Router for navigation
- Common mistakes and how to avoid them
- Best practices for clean code

### What to Learn Next

Here are recommended topics to continue your React journey, in order:

1. **TypeScript** -- TypeScript adds type checking to JavaScript. It catches many bugs before your code even runs. Most professional React projects use TypeScript. Start by learning the basics: types for strings, numbers, arrays, and objects. Then learn how to type your React components and props.

2. **Next.js** -- Next.js is a framework built on top of React. It adds features like server-side rendering (pages are prepared on the server before being sent to the browser), file-based routing (create a file and it becomes a page), and automatic code splitting (loading only the JavaScript needed for each page). Many companies use Next.js for production React apps.

3. **State Management** -- As your apps grow bigger, you might need more powerful ways to manage state. Look into:
   - **Zustand** -- A simple, lightweight state management library. Great for beginners who have outgrown `useState` and Context.
   - **Redux Toolkit** -- The most popular state management library for large applications. It has a learning curve but is used by many companies.

4. **Testing** -- Learn how to write tests for your React components. Start with:
   - **React Testing Library** -- Tests your components from the user's perspective.
   - **Jest** -- A test runner that works well with React.

5. **CSS Solutions** -- Explore different ways to style React apps:
   - **Tailwind CSS** -- A utility-first CSS framework. You add styles directly in your JSX using class names.
   - **CSS Modules** -- Scoped CSS that prevents style conflicts between components.
   - **styled-components** -- Write CSS inside your JavaScript files.

### Recommended Resources for Continued Learning

- **React Official Documentation** (react.dev) -- The official React docs are excellent. They include interactive tutorials and detailed explanations.
- **freeCodeCamp** (freecodecamp.org) -- Free courses on JavaScript, React, and web development.
- **JavaScript.info** -- The best resource for learning JavaScript deeply. Strong JavaScript skills make you a better React developer.
- **Build Projects** -- The best way to learn is to build. Here are some project ideas:
  - A to-do app with categories and due dates
  - A recipe finder that uses a food API
  - A quiz app with multiple choice questions
  - A note-taking app with local storage
  - A simple e-commerce product page

### A Final Word

Learning to code is a journey, not a destination. There will always be something new to learn. That is what makes it exciting. Do not rush. Do not compare yourself to others. Focus on understanding one thing at a time.

When you get stuck (and you will), remember:
- Read the error message carefully. It is trying to help you.
- Search for the error message online. Someone else has had the same problem.
- Take a break. Sometimes the answer comes when you step away.
- Come back to this book and review the relevant chapter.

You have the foundation now. Everything else builds on what you have learned here. Keep building. Keep learning. Keep going.

You are a React developer now.

---

## Practice Questions

1. Why do we use `event.preventDefault()` in the form submit handler?

2. What happens if we do not check `response.ok` after a fetch call?

3. Why do we set `loading` to `true` and `error` to `null` at the beginning of `handleSearch`?

4. How does the Celsius to Fahrenheit conversion work in the `WeatherCard` component?

5. Why did we create separate components (SearchBar, WeatherCard, ErrorMessage, LoadingSpinner) instead of putting everything in App?

---

## Exercises

### Exercise 1: Add More Weather Details

Add the following information to the `WeatherCard`:
- "Feels like" temperature (available at `weather.main.feels_like`)
- Minimum and maximum temperature for the day (`weather.main.temp_min` and `weather.main.temp_max`)

Make sure these also respect the Celsius/Fahrenheit toggle.

### Exercise 2: Save the Last Searched City

Use `localStorage` to save the last city the user searched for. When the app loads, automatically search for that city. Here is a hint:

```jsx
// Save to localStorage
localStorage.setItem("lastCity", city);

// Read from localStorage
const lastCity = localStorage.getItem("lastCity");
```

### Exercise 3: Add a Search History

Keep a list of the last 5 cities the user searched for. Show them as clickable buttons below the search bar. When the user clicks a city name, search for that city's weather.

---

## What Is Next?

There is no next chapter. This is the end of the book. But it is not the end of your learning. It is just the beginning. Go build something. The best way to learn React is to use React. Pick a project that excites you and start building.

Good luck, and happy coding!
