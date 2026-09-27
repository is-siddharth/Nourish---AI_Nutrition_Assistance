# 🥗 Nourish — AI Nutrition Companion

> **Know your numbers. Understand your food. Build your day.**

Nourish is an AI-powered nutrition and wellness assistant built with Python, Streamlit, Retrieval-Augmented Generation (RAG), FAISS, and a Hugging Face-hosted language model.

It combines **deterministic nutrition calculations** with **retrieved nutrition knowledge** and **AI-generated responses** to help users understand their daily nutrition needs and explore practical food choices.

> **Educational & Wellness Disclaimer**
> Nourish is a student/educational project intended for general wellness and nutrition information. Its calculations and AI-generated recommendations are estimates and are **not a substitute for professional medical advice, diagnosis, or treatment.**

---

# 🌱 Why I Built Nourish

Nutrition advice is everywhere.

The difficult part isn't finding *more* information — it's making that information useful for a specific person.

A user may want to know:

* How many calories might I need in a day?
* What does my BMR mean?
* What is TDEE?
* What could a simple day of meals look like?
* What are good sources of protein?
* What foods fit a vegetarian or vegan diet?
* Can I ask an AI about a nutrition topic and get an answer grounded in a knowledge source?

Nourish was built as an attempt to bring these pieces together in one simple application.

The project also explores a more important question:

> **How can an AI application combine traditional Python logic, a knowledge base, retrieval, and a language model instead of relying on an LLM for everything?**

That distinction is central to the project.

---

# 🥗 What Exactly Does Nourish Do?

Nourish has two main experiences.

## 1. Build My Day

The user provides a basic profile:

* Age
* Gender
* Height
* Weight
* Activity level
* Goal
* Diet preference
* Food allergies

Nourish then calculates:

### BMI

Body Mass Index based on height and weight.

### BMR

Estimated Basal Metabolic Rate using the **Mifflin-St Jeor equation**.

### TDEE

Estimated Total Daily Energy Expenditure based on BMR and an activity factor.

### Daily Calorie Target

An estimated target adjusted according to the selected goal.

These values are then combined with the user's preferences and relevant nutrition knowledge retrieved from the project's knowledge base.

The AI generates a simple one-day plan containing:

1. Breakfast
2. Morning Snack
3. Lunch
4. Evening Snack
5. Dinner

Each meal includes approximate:

* Food items
* Portions
* Calories
* Protein

---

# 💬 2. Ask Nourish

Users can ask general nutrition questions such as:

> "What are some good vegetarian sources of protein?"

or:

> "What foods are high in fiber?"

or:

> "Why is hydration important?"

Instead of sending the question directly to the language model, Nourish first searches its nutrition knowledge base using **Retrieval-Augmented Generation (RAG)**.

The relevant information is then provided to the language model as context.

This gives the application a simple architecture:


BMI = weight (kg) / height² (m²)

---

# 🧠 How the AI Part Works

Nourish is not simply:

```text
User → LLM → Answer
```

The project combines three different types of logic.

## 1. Deterministic Python logic

Python handles calculations such as:

```text
BMI
BMR
TDEE
Calorie Target
```

These calculations don't need an AI model.

---

## 2. Retrieval-Augmented Generation

## RAG Pipeline

```text
data/nutrition.pdf
```

The PDF is processed into smaller text chunks.

Those chunks are converted into numerical representations called **embeddings**.

The embeddings are stored in a FAISS vector index.

When a user asks a question, Nourish searches the vector database for the most relevant pieces of information.

---

## Project Structure
ai_health_assistant_project/
│
├── app.py
├── diet.py
├── rag.py
├── create_database.py
├── llm_test.py
├── prompt.md
├── readme.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── nutrition.pdf
│
└── vector_db/
    ├── index.faiss
    └── index.pkl
```

## What each file does

### `app.py`

The main Streamlit application.

Responsible for:

* User interface
* User profile input
* Nutrition dashboard
* Diet recommendation workflow
* Nutrition chatbot
* LLM interaction
* Displaying retrieved knowledge

---

### `diet.py`

Contains the deterministic nutrition calculations.

Responsible for:

* BMI
* BMR
* TDEE
* Calorie target
* Input validation
* Nutrition profile calculation

The language model is **not** used for these calculations.

---

### `rag.py`

Contains the RAG infrastructure.

Responsible for:

* Loading the nutrition PDF
* Splitting documents into chunks
* Creating embeddings
* Creating the FAISS vector database
* Loading the vector database
* Searching for relevant nutrition knowledge
* Preparing retrieved context for the LLM

---

### `create_database.py`

A utility script used to create/rebuild the FAISS knowledge database.

It processes:

```text
data/nutrition.pdf
```

and creates:

```text
vector_db/
├── index.faiss
└── index.pkl
```

Run it whenever the source nutrition PDF changes.

---

### `llm_test.py`

A standalone diagnostic script for testing the LLM + RAG pipeline outside Streamlit.

It helps verify that:

* The API credential is available
* The model endpoint works
* The RAG database can retrieve information
* Retrieved information can be sent to the language model
* The model returns a response

---

### `prompt.md`

Contains prompt-related notes and experimentation used during development.

---

### `requirements.txt`

Contains the Python dependencies required to run the project.

---

### `data/nutrition.pdf`

The project's nutrition knowledge source.

This document is processed and converted into a searchable vector database.

---

### `vector_db/`

The generated FAISS vector database.

It is created locally from the nutrition PDF and does not need to be manually written.

---

# ⚙️ How to Run the Project

## 1. Clone the repository

```bash
git clone <repository-url>
cd ai_health_assistant_project
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv env
source env/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 API Configuration

Create a `.env` file in the project root:

```text
HF_TOKEN=your_hugging_face_token
```

The token is used to access the Hugging Face model endpoint.

**Do not commit `.env` or API credentials to GitHub.**

---

# 🗂️ Create the RAG Database

Before starting the application, create the local FAISS database:

```bash
python create_database.py
```

The script reads:

```text
data/nutrition.pdf
```

and creates:

```text
vector_db/
├── index.faiss
└── index.pkl
```

You normally only need to repeat this step when the source PDF changes.

---

# ▶️ Start Nourish

Run:

```bash
streamlit run app.py
```

Streamlit will start the application and provide a local web address.

---

# 🧪 Test the AI Pipeline Separately

If you want to test the LLM and RAG pipeline without starting the Streamlit application:

```bash
python llm_test.py
```

This provides a simple way to verify that the AI pipeline is working independently of the UI.

---

# 🧮 Nutrition Calculations

Nourish currently uses the following calculations.

## BMI

```text
BMI = weight (kg) / height² (m²)
```

---

## BMR

Nourish uses the **Mifflin-St Jeor equation**.

For males:

```text
BMR = 10 × weight
    + 6.25 × height
    - 5 × age
    + 5
```

For females:

```text
BMR = 10 × weight
    + 6.25 × height
    - 5 × age
    - 161
```

Height is provided to the calculation in centimetres.

---

## TDEE

```text
TDEE = BMR × Activity Factor
```

The current activity factors are:

| Activity Level    | Factor |
| ----------------- | -----: |
| Sedentary         |   1.20 |
| Lightly Active    |  1.375 |
| Moderately Active |   1.55 |
| Very Active       |  1.725 |
| Extra Active      |   1.90 |

---

## Calorie Target

The current project uses simple goal-based adjustments:

| Goal            | Current Project Adjustment |
| --------------- | -------------------------: |
| Weight maintain |                       TDEE |
| Weight loss     |            TDEE − 400 kcal |
| Weight gain     |            TDEE + 300 kcal |

These are **project assumptions**, not universal medical or nutritional prescriptions.

---

# 🛡️ Safety & Limitations

Nourish is intentionally positioned as a **general wellness and nutrition application**, not a medical system.

The application does not:

* Diagnose diseases
* Prescribe medicines
* Claim to cure medical conditions
* Replace a doctor or registered dietitian
* Provide emergency medical advice

The BMI, BMR, TDEE and calorie values are estimates.

AI-generated meal recommendations are also approximate and should not be treated as individualized clinical nutrition plans.

For medical conditions, allergies requiring medical management, eating disorders, pregnancy-related nutrition, or other specialized circumstances, users should consult an appropriately qualified healthcare professional.

---

# 🎯 What This Project Demonstrates

Although Nourish is a relatively small application, it brings together several important concepts in modern data and AI applications:

### Traditional programming

Deterministic calculations and validation are handled directly by Python.

### Data processing

The nutrition PDF is loaded and transformed into searchable text chunks.

### Embeddings

Text is converted into numerical vector representations.

### Vector search

FAISS finds information that is semantically similar to a user's question.

### Retrieval-Augmented Generation

Retrieved knowledge is supplied to the language model as context.

### Large Language Models

The model turns structured information and retrieved context into natural-language responses.

### Application development

Streamlit brings the complete pipeline together into an interactive product.

---

# 🚧 Current Scope

Nourish is intentionally a relatively lightweight project.

It currently focuses on:

* Basic nutrition calculations
* One-day meal recommendations
* General nutrition questions
* PDF-based RAG
* FAISS vector search
* LLM-generated responses
* Streamlit-based interaction

It is not intended to be a production healthcare platform.

---

# 🔮 Possible Future Improvements

The project can be extended in several directions.

### Better recommendation structure

Instead of relying entirely on free-form LLM output, meal recommendations could be returned as structured data and rendered as dedicated meal cards.

### Stronger recommendation validation

Generated meal plans could be checked programmatically for:

* Allergens
* Diet compatibility
* Calorie ranges
* Protein targets
* Missing meals

### Better RAG evaluation

Retrieval quality could be evaluated using a collection of test questions and expected relevant documents.

### Improved knowledge management

The nutrition knowledge source could eventually be expanded beyond a single PDF.

### User history

A future version could allow users to save previous nutrition profiles and recommendations.

### More advanced nutrition planning

The system could potentially incorporate additional nutritional targets such as:

* Protein
* Fiber
* Carbohydrates
* Fats
* Micronutrients

### Better AI observability

The application could expose more information about:

* Retrieved chunks
* Retrieval scores
* Prompt construction
* Model response
* Validation results

This would make the system easier to evaluate and debug.

---

# 📌 Project Philosophy

The core idea behind Nourish is simple:

> **Use traditional programming where deterministic logic is enough, use retrieval when the application needs relevant knowledge, and use an LLM where natural-language reasoning and communication add value.**

The project therefore does not treat the language model as the entire application.

Instead:

```text
Python
    ↓
Calculations & validation

RAG
    ↓
Relevant knowledge

LLM
    ↓
Natural-language generation

Streamlit
<<<<<<< HEAD
FAISS
RAG (Retrieval-Augmented Generation)
Large Language Model API
Hugging Face
python-dotenv
Nutrition knowledge base in PDF format
=======
    ↓
User experience
```

Together, these components form **Nourish — an AI nutrition companion designed to make everyday nutrition information easier to understand and use.**
>>>>>>> b59f872 (Version Updated and Redesigned)
