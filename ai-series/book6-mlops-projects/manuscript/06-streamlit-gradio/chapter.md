# Chapter 6: Building ML Demos with Streamlit and Gradio

## What You Will Learn

In this chapter, you will learn:

- What Streamlit is and how to build interactive apps with it
- How to use st.write, st.slider, st.file_uploader, and other widgets
- What Gradio is and how to create ML interfaces quickly
- How to use Gradio's Interface and Blocks for complex layouts
- How to build complete ML demos with both tools
- How to share your demos publicly with the world

## Why This Chapter Matters

Imagine you build an amazing model that can predict house prices. You show it to your manager by running a Python script in the terminal. They stare at the black screen with numbers scrolling by and say, "That is nice, but can you make it... easier to use?"

Non-technical people do not want to run Python scripts. They want to click buttons, drag sliders, and see results in a nice interface. Streamlit and Gradio let you build these interfaces in minutes, not weeks.

Think of Streamlit and Gradio as "Instagram filters for your ML model." They take something technical and make it accessible and visual.

---

## Part 1: Streamlit

Streamlit turns Python scripts into interactive web apps. You write Python, and Streamlit handles all the web development.

### Installing Streamlit

```bash
pip install streamlit
```

### Your First Streamlit App

```python
"""
app_hello.py - Your first Streamlit application.

Run with: streamlit run app_hello.py

Streamlit will open a browser window automatically.
"""

import streamlit as st

# st.title creates a large heading
st.title("My First Streamlit App")

# st.write is the Swiss army knife of Streamlit
# It can display text, data, charts, and more
st.write("Hello, World! Welcome to Streamlit.")

# st.markdown supports Markdown formatting
st.markdown("""
### What Can Streamlit Do?
- Display **text** and *formatting*
- Show data in tables
- Create interactive widgets
- Display charts and visualizations
""")

# Display a simple calculation
x = 5
y = 10
st.write(f"The sum of {x} and {y} is {x + y}")
```

To run this app:

```bash
streamlit run app_hello.py
```

```
Output (in terminal):
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

### Streamlit Widgets

Widgets are interactive elements that let users provide input:

```python
"""
app_widgets.py - Streamlit widget examples.

Run with: streamlit run app_widgets.py

Each widget returns the current value selected by the user.
When a user changes a widget, Streamlit re-runs the entire
script with the new values.
"""

import streamlit as st

st.title("Streamlit Widget Gallery")

# ============================================================
# Text Input
# ============================================================
st.header("Text Input")

# st.text_input creates a text field
name = st.text_input("What is your name?", value="Alice")
st.write(f"Hello, {name}!")

# st.text_area creates a larger text field
feedback = st.text_area(
    "Tell us about your experience:",
    height=100,
)
if feedback:
    st.write(f"You wrote {len(feedback)} characters")

# ============================================================
# Numbers
# ============================================================
st.header("Number Input")

# st.slider creates a slider
age = st.slider(
    "Select your age:",
    min_value=0,
    max_value=100,
    value=25,
    step=1,
)
st.write(f"Your age: {age}")

# st.number_input creates a number field with +/- buttons
income = st.number_input(
    "Annual income ($):",
    min_value=0,
    max_value=1000000,
    value=50000,
    step=1000,
)

# ============================================================
# Selection
# ============================================================
st.header("Selection Widgets")

# st.selectbox creates a dropdown menu
model_type = st.selectbox(
    "Choose a model:",
    options=["Random Forest", "Logistic Regression", "Neural Network"],
)
st.write(f"You selected: {model_type}")

# st.multiselect lets users pick multiple options
features = st.multiselect(
    "Select features to use:",
    options=["Age", "Income", "Credit Score", "Employment Years"],
    default=["Age", "Income"],
)
st.write(f"Selected features: {features}")

# st.radio creates radio buttons
difficulty = st.radio(
    "Difficulty level:",
    options=["Easy", "Medium", "Hard"],
)

# ============================================================
# Toggles
# ============================================================
st.header("Toggles")

# st.checkbox creates a checkbox
show_details = st.checkbox("Show detailed output")
if show_details:
    st.write("Here are the details you requested!")

# ============================================================
# File Upload
# ============================================================
st.header("File Upload")

# st.file_uploader creates a file upload widget
uploaded_file = st.file_uploader(
    "Upload a CSV file:",
    type=["csv"],  # Only allow CSV files
)

if uploaded_file is not None:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    st.write(f"Uploaded file has {len(df)} rows and {len(df.columns)} columns")
    st.dataframe(df.head())  # Display the first 5 rows as a table

# ============================================================
# Buttons
# ============================================================
st.header("Buttons")

if st.button("Click me!"):
    st.write("Button was clicked!")
    st.balloons()  # Fun animation!
```

### Building an ML Demo with Streamlit

```python
"""
app_ml_demo.py - Complete ML prediction demo with Streamlit.

Run with: streamlit run app_ml_demo.py

This app lets users input features and see predictions
from a trained ML model.
"""

import streamlit as st
import joblib
import numpy as np
import pandas as pd

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="ML Prediction Demo",
    page_icon="🤖",
    layout="wide",  # Use the full width of the page
)

st.title("Credit Risk Prediction")
st.write("Enter the customer details below to predict credit risk.")


# ============================================================
# Load Model (cached so it only loads once)
# ============================================================
@st.cache_resource  # Cache the model so it does not reload on every interaction
def load_model():
    """
    Load the trained ML model.

    @st.cache_resource tells Streamlit to load this once
    and reuse it. Without this decorator, the model would
    reload every time a user moves a slider!
    """
    try:
        model = joblib.load("models/trained_model.pkl")
        return model
    except FileNotFoundError:
        return None


model = load_model()

if model is None:
    st.error("Model file not found! Please train a model first.")
    st.stop()  # Stop the app here


# ============================================================
# User Input (Sidebar)
# ============================================================
st.sidebar.header("Customer Details")

# Sidebar widgets keep the main area clean
age = st.sidebar.slider("Age", 18, 80, 35)
income = st.sidebar.number_input(
    "Annual Income ($)", 10000, 500000, 50000, step=5000
)
credit_score = st.sidebar.slider("Credit Score", 300, 850, 650)
employment_years = st.sidebar.slider("Years Employed", 0, 40, 5)


# ============================================================
# Make Prediction
# ============================================================
# Prepare features
features = np.array([[age, income, credit_score, employment_years]])

# Predict
prediction = model.predict(features)[0]
try:
    probability = model.predict_proba(features)[0]
except AttributeError:
    probability = [1 - prediction, prediction]

# ============================================================
# Display Results
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Risk Prediction",
        value="High Risk" if prediction == 1 else "Low Risk",
    )

with col2:
    st.metric(
        label="Risk Probability",
        value=f"{probability[1]:.1%}",
    )

with col3:
    risk_level = (
        "Low" if probability[1] < 0.3
        else "Medium" if probability[1] < 0.7
        else "High"
    )
    st.metric(label="Risk Level", value=risk_level)

# Progress bar showing risk level
st.subheader("Risk Score")
st.progress(float(probability[1]))

# Show input summary
st.subheader("Customer Summary")
summary_df = pd.DataFrame({
    "Feature": ["Age", "Income", "Credit Score", "Employment Years"],
    "Value": [age, f"${income:,}", credit_score, employment_years],
})
st.table(summary_df)

# ============================================================
# Batch Prediction from File Upload
# ============================================================
st.subheader("Batch Prediction")
st.write("Upload a CSV file with columns: age, income, credit_score, employment_years")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(f"Loaded {len(df)} records")

    # Make predictions for all rows
    predictions = model.predict(df.values)
    try:
        probabilities = model.predict_proba(df.values)[:, 1]
    except AttributeError:
        probabilities = predictions.astype(float)

    # Add predictions to the dataframe
    df["prediction"] = predictions
    df["risk_probability"] = probabilities
    df["risk_label"] = df["risk_probability"].apply(
        lambda p: "Low" if p < 0.3 else "Medium" if p < 0.7 else "High"
    )

    # Display results
    st.dataframe(df)

    # Summary statistics
    st.subheader("Prediction Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("High Risk", int((predictions == 1).sum()))
    with col3:
        st.metric("Low Risk", int((predictions == 0).sum()))
```

---

## Part 2: Gradio

Gradio is another tool for building ML demos. It is especially popular in the ML research community because it creates interfaces with just a few lines of code.

### Installing Gradio

```bash
pip install gradio
```

### Gradio Interface: The Simple Way

```python
"""
gradio_hello.py - Your first Gradio application.

Run with: python gradio_hello.py

Gradio's Interface class creates a complete UI from
just three things:
1. A function to run
2. Input components
3. Output components
"""

import gradio as gr


def greet(name, intensity):
    """
    A simple greeting function.

    Gradio will create input widgets automatically based
    on the function's parameters and type hints.
    """
    return f"Hello, {name}! " + "!" * intensity


# Create the interface
# fn: the function to call
# inputs: what the user provides
# outputs: what we show back
demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Your Name", placeholder="Enter your name"),
        gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Enthusiasm"),
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting Generator",
    description="Enter your name and choose your enthusiasm level!",
)

# Launch the app
demo.launch()
```

```
Output:
Running on local URL: http://127.0.0.1:7860
```

### Gradio for ML Predictions

```python
"""
gradio_ml.py - ML prediction interface with Gradio.

Run with: python gradio_ml.py

This creates a simple interface where users enter
features and get a risk prediction.
"""

import gradio as gr
import joblib
import numpy as np


# Load model
try:
    model = joblib.load("models/trained_model.pkl")
except FileNotFoundError:
    model = None


def predict_risk(age, income, credit_score, employment_years):
    """
    Make a credit risk prediction.

    Each parameter corresponds to a Gradio input widget.
    The function returns values that map to output widgets.
    """
    if model is None:
        return "Model not loaded", 0.0, "Error"

    # Prepare features
    features = np.array([[age, income, credit_score, employment_years]])

    # Make prediction
    prediction = model.predict(features)[0]

    try:
        probability = model.predict_proba(features)[0][1]
    except AttributeError:
        probability = float(prediction)

    # Determine risk level
    if probability < 0.3:
        risk_level = "Low Risk"
    elif probability < 0.7:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    result_text = f"Prediction: {risk_level}"
    confidence = round(probability * 100, 1)

    return result_text, confidence, risk_level


# Create the interface
demo = gr.Interface(
    fn=predict_risk,
    inputs=[
        gr.Slider(18, 80, value=35, step=1, label="Age"),
        gr.Number(value=50000, label="Annual Income ($)"),
        gr.Slider(300, 850, value=650, step=10, label="Credit Score"),
        gr.Slider(0, 40, value=5, step=1, label="Years Employed"),
    ],
    outputs=[
        gr.Textbox(label="Prediction"),
        gr.Number(label="Risk Probability (%)"),
        gr.Textbox(label="Risk Level"),
    ],
    title="Credit Risk Predictor",
    description="Enter customer details to predict credit risk.",
    examples=[
        [25, 40000, 620, 2],   # Young, low income, low credit
        [45, 95000, 780, 15],  # Middle-aged, good income, high credit
        [60, 150000, 810, 30], # Senior, high income, excellent credit
    ],
)

demo.launch()
```

```
Output:
Running on local URL: http://127.0.0.1:7860
```

### Gradio Blocks: More Control

`gr.Interface` is simple but limited. `gr.Blocks` gives you full control over the layout:

```python
"""
gradio_blocks.py - Advanced Gradio layout with Blocks.

Run with: python gradio_blocks.py

Blocks lets you create custom layouts with rows, columns,
tabs, and more. It is like the difference between a
pre-built house (Interface) and designing your own (Blocks).
"""

import gradio as gr
import joblib
import numpy as np
import pandas as pd


# Load model
try:
    model = joblib.load("models/trained_model.pkl")
    model_loaded = True
except FileNotFoundError:
    model_loaded = False


def single_predict(age, income, credit_score, emp_years):
    """Make a single prediction."""
    if not model_loaded:
        return "Model not loaded", "N/A", "N/A"

    features = np.array([[age, income, credit_score, emp_years]])
    prediction = model.predict(features)[0]

    try:
        probability = model.predict_proba(features)[0][1]
    except AttributeError:
        probability = float(prediction)

    risk = "Low" if probability < 0.3 else "Medium" if probability < 0.7 else "High"

    return (
        f"{'High' if prediction == 1 else 'Low'} Risk",
        f"{probability:.1%}",
        risk,
    )


def batch_predict(file):
    """Make predictions for a CSV file."""
    if not model_loaded:
        return None

    df = pd.read_csv(file.name)
    predictions = model.predict(df.values)

    try:
        probabilities = model.predict_proba(df.values)[:, 1]
    except AttributeError:
        probabilities = predictions.astype(float)

    df["prediction"] = predictions
    df["probability"] = probabilities
    df["risk"] = df["probability"].apply(
        lambda p: "Low" if p < 0.3 else "Medium" if p < 0.7 else "High"
    )

    return df


# Build the interface with Blocks
with gr.Blocks(title="ML Risk Predictor") as demo:
    gr.Markdown("# Credit Risk Prediction Tool")
    gr.Markdown("Predict credit risk using our trained model.")

    # Tabs for different features
    with gr.Tabs():
        # Tab 1: Single Prediction
        with gr.TabItem("Single Prediction"):
            with gr.Row():
                # Left column: inputs
                with gr.Column():
                    gr.Markdown("### Customer Details")
                    age = gr.Slider(18, 80, value=35, step=1, label="Age")
                    income = gr.Number(value=50000, label="Income ($)")
                    credit = gr.Slider(300, 850, value=650, step=10, label="Credit Score")
                    emp = gr.Slider(0, 40, value=5, step=1, label="Employment Years")
                    predict_btn = gr.Button("Predict", variant="primary")

                # Right column: outputs
                with gr.Column():
                    gr.Markdown("### Prediction Results")
                    pred_output = gr.Textbox(label="Prediction")
                    prob_output = gr.Textbox(label="Probability")
                    risk_output = gr.Textbox(label="Risk Level")

            # Connect button to function
            predict_btn.click(
                fn=single_predict,
                inputs=[age, income, credit, emp],
                outputs=[pred_output, prob_output, risk_output],
            )

        # Tab 2: Batch Prediction
        with gr.TabItem("Batch Prediction"):
            gr.Markdown("### Upload CSV for Batch Predictions")
            gr.Markdown(
                "CSV should have columns: age, income, "
                "credit_score, employment_years"
            )
            file_input = gr.File(label="Upload CSV")
            batch_output = gr.Dataframe(label="Results")

            file_input.change(
                fn=batch_predict,
                inputs=file_input,
                outputs=batch_output,
            )

        # Tab 3: Model Info
        with gr.TabItem("About"):
            gr.Markdown("""
            ### About This Model
            - **Type:** Random Forest Classifier
            - **Features:** Age, Income, Credit Score, Employment Years
            - **Output:** Binary risk prediction (Low/High)
            """)
            status = "Loaded" if model_loaded else "Not Loaded"
            gr.Markdown(f"**Model Status:** {status}")


demo.launch()
```

---

## Sharing Your Demos Publicly

Both Streamlit and Gradio offer ways to share your demo with anyone in the world.

### Sharing Gradio with a Public Link

```python
"""
gradio_share.py - Share your Gradio demo publicly.

The share=True parameter creates a temporary public URL
that anyone can access for 72 hours.
"""

import gradio as gr


def predict(text):
    return f"You entered: {text}"


demo = gr.Interface(
    fn=predict,
    inputs="text",
    outputs="text",
)

# share=True creates a public link
# The link works for 72 hours
demo.launch(share=True)
```

```
Output:
Running on local URL: http://127.0.0.1:7860
Running on public URL: https://abc123xyz.gradio.live

This share link expires in 72 hours.
```

### Sharing Streamlit with Streamlit Cloud

Streamlit offers free hosting through Streamlit Cloud:

```
+--------------------------------------------------+
|  Sharing Streamlit Apps                           |
|                                                   |
|  1. Push your code to GitHub                     |
|  2. Go to share.streamlit.io                     |
|  3. Connect your GitHub repo                     |
|  4. Select the Python file to run                |
|  5. Click Deploy!                                |
|                                                   |
|  Your app gets a public URL like:                |
|  https://your-app.streamlit.app                  |
+--------------------------------------------------+
```

---

## Streamlit vs Gradio Comparison

```
+----------------------------------------------------------------+
|  Feature          | Streamlit           | Gradio               |
|-------------------|---------------------|----------------------|
|  Ease of Use      | Very easy           | Very easy            |
|  Code Needed      | More code           | Less code            |
|  Customization    | High                | Medium               |
|  Best For         | Data dashboards     | ML model demos       |
|  Sharing          | Streamlit Cloud     | gradio.live or HF    |
|  Layout Control   | Good (columns,tabs) | Good (Blocks)        |
|  File Upload      | st.file_uploader    | gr.File              |
|  Live Updates     | Re-runs script      | Event-driven         |
|  API Auto-gen     | No                  | Yes (built-in API)   |
+----------------------------------------------------------------+
```

---

## Common Mistakes

1. **Not caching model loading in Streamlit.** Without `@st.cache_resource`, the model reloads every time a user interacts with a widget. This makes the app very slow.

2. **Forgetting that Streamlit re-runs the entire script.** Every time a user changes a widget, Streamlit runs the whole Python file from top to bottom. Design your code with this in mind.

3. **Making demos too complex.** The goal is a simple demonstration, not a full application. Keep it focused.

4. **Not providing example inputs.** Users often do not know what values to enter. Provide examples so they can try your model immediately.

5. **Not handling errors gracefully.** Show friendly error messages when the model file is missing or input is invalid.

---

## Best Practices

1. **Use caching for expensive operations.** In Streamlit, use `@st.cache_resource` for models and `@st.cache_data` for data loading.

2. **Provide example inputs.** Both Streamlit and Gradio support examples that users can click to try.

3. **Add descriptions and help text.** Explain what each input means and what values are expected.

4. **Use a sidebar for inputs in Streamlit.** This keeps the main area clean for showing results.

5. **Test with different input values.** Make sure your demo handles edge cases gracefully.

---

## Quick Summary

Streamlit and Gradio are tools for building interactive ML demos quickly. Streamlit is great for data-heavy dashboards with more customization. Gradio excels at creating simple ML interfaces with minimal code. Both can be shared publicly. Use them to make your ML models accessible to non-technical users.

---

## Key Points

- Streamlit turns Python scripts into interactive web apps
- st.cache_resource prevents reloading the model on every interaction
- Gradio's Interface class creates a UI from a function, inputs, and outputs
- Gradio's Blocks class gives more control over layout
- Both tools support file uploads for batch predictions
- Gradio can create temporary public links with share=True
- Streamlit apps can be deployed to Streamlit Cloud for free

---

## Practice Questions

1. What does `@st.cache_resource` do and why is it important when loading ML models in Streamlit?

2. What are the three things you need to provide to `gr.Interface` to create a Gradio app?

3. How does Streamlit handle user interactions differently from Gradio?

4. When would you choose Streamlit over Gradio? When would you choose Gradio over Streamlit?

5. How can you share a Gradio demo with someone who does not have Python installed?

---

## Exercises

### Exercise 1: Streamlit Dashboard

Build a Streamlit app that:
- Lets users upload a CSV file
- Shows basic statistics (mean, median, min, max for each column)
- Displays a histogram for a user-selected column
- Shows the first 10 rows of data

### Exercise 2: Gradio Model Demo

Create a Gradio interface for an image classification model that:
- Accepts an image upload
- Shows the top 3 predicted classes with confidence scores
- Includes at least 3 example images

### Exercise 3: Side-by-Side Comparison

Build the same ML demo in both Streamlit and Gradio. Compare:
- Lines of code needed
- Ease of adding new features
- Look and feel of the interface

---

## What Is Next?

Now you can build beautiful demos for your ML models. But demos handle one request at a time. What about serving predictions to thousands of users simultaneously? In Chapter 7, we will learn about model serving patterns: batch vs real-time inference, scaling strategies, and caching predictions for speed.
