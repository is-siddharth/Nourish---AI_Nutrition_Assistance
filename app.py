import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from diet import calculate_nutrition_profile
from rag import build_context, search_nutrition


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "Nourish"
APP_TAGLINE = "Know your numbers. Understand your food. Build your day."

MODEL_NAME = "openai/gpt-oss-120b"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nourish — AI Nutrition Companion",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

        .main-title {
            font-size: 3rem;
            font-weight: 750;
            margin-bottom: 0.1rem;
        }

        .tagline {
            font-size: 1.15rem;
            color: #6b7280;
            margin-bottom: 1.25rem;
        }

        .section-label {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #6b7280;
            margin-bottom: 0.15rem;
        }

        .small-note {
            font-size: 0.82rem;
            color: #6b7280;
        }

        .feature-card {
            padding: 1rem;
            border: 1px solid rgba(128, 128, 128, 0.18);
            border-radius: 12px;
            background: rgba(128, 128, 128, 0.035);
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LLM CLIENT
# ============================================================

@st.cache_resource
def get_llm_client():
    """
    Create and cache the OpenAI-compatible Hugging Face client.
    """

    if not HF_TOKEN:
        return None

    return OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )


client = get_llm_client()


# ============================================================
# SESSION STATE
# ============================================================

if "diet_response" not in st.session_state:
    st.session_state.diet_response = None

if "diet_sources" not in st.session_state:
    st.session_state.diet_sources = []

if "chat_response" not in st.session_state:
    st.session_state.chat_response = None

if "chat_sources" not in st.session_state:
    st.session_state.chat_sources = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f'<div class="main-title">🥗 {APP_NAME}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="tagline">{APP_TAGLINE}</div>',
    unsafe_allow_html=True,
)

st.write(
    "A wellness-focused AI nutrition companion that combines "
    "nutrition calculations, trusted knowledge retrieval, and "
    "AI-generated guidance for everyday food decisions."
)

st.divider()


# ============================================================
# SIDEBAR — PROFILE
# ============================================================

st.sidebar.title("Your Profile")

st.sidebar.caption(
    "Give Nourish a few details about yourself. "
    "They help shape your nutrition estimates and recommendations."
)

with st.sidebar.form("profile_form"):

    gender = st.selectbox(
        "Gender",
        ["male", "female"],
        format_func=lambda value: value.capitalize(),
    )

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=100,
        value=25,
        step=1,
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=200.0,
        value=70.0,
        step=0.5,
    )

    height = st.number_input(
        "Height (cm)",
        min_value=100.0,
        max_value=250.0,
        value=170.0,
        step=0.5,
    )

    activity = st.selectbox(
        "Activity level",
        [
            "Sedentary",
            "Lightly_Active",
            "Moderately_Active",
            "Very_Active",
            "Extra_Active",
        ],
        format_func=lambda value: value.replace("_", " "),
    )

    aim = st.selectbox(
        "Your goal",
        [
            "weight maintain",
            "weight loss",
            "weight gain",
        ],
        format_func=lambda value: value.title(),
    )

    diet_type = st.selectbox(
        "Diet preference",
        [
            "Vegetarian",
            "Non-Vegetarian",
            "Vegan",
        ],
    )

    allergies = st.multiselect(
        "Food allergies",
        [
            "None",
            "Peanuts",
            "Tree nuts",
            "Milk",
            "Eggs",
            "Soy",
            "Wheat",
            "Fish",
            "Shellfish",
        ],
        default=["None"],
    )

    update_profile = st.form_submit_button(
        "Update My Profile",
        use_container_width=True,
    )


# ============================================================
# ALLERGY NORMALIZATION
# ============================================================

if "None" in allergies and len(allergies) > 1:
    allergies = [
        allergy
        for allergy in allergies
        if allergy != "None"
    ]

allergy_text = ", ".join(allergies) if allergies else "None"


# ============================================================
# NUTRITION CALCULATIONS
# ============================================================

try:

    nutrition = calculate_nutrition_profile(
        weight=weight,
        height=height,
        age=age,
        gender=gender,
        activity=activity,
        aim=aim,
    )

    bmi = nutrition["bmi"]
    bmr = nutrition["bmr"]
    tdee = nutrition["tdee"]
    calorie = nutrition["calorie_target"]

except Exception as error:

    st.error(
        "Nourish couldn't calculate your nutrition profile."
    )

    with st.expander("Technical details"):
        st.exception(error)

    st.stop()


# ============================================================
# HEALTH SNAPSHOT
# ============================================================

st.markdown(
    '<div class="section-label">Your snapshot</div>',
    unsafe_allow_html=True,
)

st.subheader("What your numbers look like")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        "BMI",
        f"{bmi:.1f}",
    )

with metric_col2:
    st.metric(
        "BMR",
        f"{bmr:.0f} kcal",
    )

with metric_col3:
    st.metric(
        "TDEE",
        f"{tdee:.0f} kcal",
    )

with metric_col4:
    st.metric(
        "Daily Target",
        f"{calorie:.0f} kcal",
    )


info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:
    st.caption("BMI")
    st.write(
        "A weight-to-height ratio commonly used as a broad screening measure."
    )

with info_col2:
    st.caption("BMR")
    st.write(
        "Estimated energy your body uses at rest."
    )

with info_col3:
    st.caption("TDEE")
    st.write(
        "Estimated daily energy expenditure after accounting for activity."
    )

with info_col4:
    st.caption("Daily Target")
    st.write(
        "An estimated calorie target adjusted for your selected goal."
    )


st.caption(
    "These values are estimates for general wellness purposes, "
    "not medical measurements."
)

st.divider()


# ============================================================
# MAIN TABS
# ============================================================

diet_tab, assistant_tab = st.tabs(
    [
        "🥗 Build My Day",
        "💬 Ask Nourish",
    ]
)


# ============================================================
# TAB 1 — DIET RECOMMENDATION
# ============================================================

with diet_tab:

    st.markdown(
        '<div class="section-label">Personalized nutrition</div>',
        unsafe_allow_html=True,
    )

    st.header("Build a day around your goal")

    st.write(
        "Nourish combines your profile, estimated calorie target, "
        "diet preference, food restrictions, and nutrition knowledge "
        "to create a simple one-day meal plan."
    )

    profile_col1, profile_col2, profile_col3 = st.columns(3)

    with profile_col1:
        st.caption("Goal")
        st.write(aim.title())

    with profile_col2:
        st.caption("Diet")
        st.write(diet_type)

    with profile_col3:
        st.caption("Avoid")
        st.write(allergy_text)

    st.write("")

    generate_plan = st.button(
        "Create My One-Day Plan",
        type="primary",
        use_container_width=True,
    )

    if generate_plan:

        if client is None:

            st.error(
                "The AI service isn't configured. "
                "Please make sure HF_TOKEN is available in your environment."
            )

        else:

            status = st.status(
                "🥗 Nourish is putting your day together...",
                expanded=True,
            )

            try:

                # ------------------------------------------------
                # STEP 1 — PROFILE
                # ------------------------------------------------

                status.write(
                    "✓ Profile understood"
                )

                # ------------------------------------------------
                # STEP 2 — NUTRITION CALCULATIONS
                # ------------------------------------------------

                status.write(
                    "✓ Nutrition targets calculated"
                )

                # ------------------------------------------------
                # STEP 3 — RAG RETRIEVAL
                # ------------------------------------------------

                status.write(
                    "📚 Looking through the nutrition knowledge base..."
                )

                search_query = f"""
                Healthy nutrition and meal recommendations for:

                Diet type: {diet_type}
                Goal: {aim}
                Target calories: {calorie} kcal
                Protein-rich foods
                Balanced meals
                Foods to avoid: {allergy_text}
                """

                docs = search_nutrition(
                    search_query,
                    k=3,
                )

                if not docs:
                    raise RuntimeError(
                        "No relevant nutrition knowledge was retrieved."
                    )

                context = build_context(docs)

                status.write(
                    f"✓ Found {len(docs)} relevant knowledge sections"
                )

                # ------------------------------------------------
                # STEP 4 — LLM GENERATION
                # ------------------------------------------------

                status.write(
                    "🧠 Nourish is building your plan..."
                )

                prompt = f"""
You are Nourish, a careful nutrition and wellness assistant.

Create a simple, practical one-day meal plan using the user's
profile and the retrieved nutrition knowledge.

RETRIEVED NUTRITION KNOWLEDGE
-----------------------------
{context}

USER PROFILE
------------
Age: {age}
Gender: {gender}
Height: {height} cm
Weight: {weight} kg
Activity level: {activity}
Goal: {aim}
Diet type: {diet_type}
Food allergies/restrictions: {allergy_text}

ESTIMATED VALUES
----------------
BMI: {bmi}
BMR: {bmr} kcal/day
TDEE: {tdee} kcal/day
Estimated daily calorie target: {calorie} kcal/day

CREATE
------
Create five meals:

1. Breakfast
2. Morning Snack
3. Lunch
4. Evening Snack
5. Dinner

For every meal provide:

- Food items
- Approximate portion
- Approximate calories
- Approximate protein

IMPORTANT
---------
- Respect the selected diet type.
- Do not recommend any stated allergen.
- Keep the meals practical and easy to understand.
- Aim to keep the overall plan reasonably close to the
  estimated daily calorie target.
- Prioritize balanced meals and reasonable protein intake.
- Use the retrieved nutrition knowledge when relevant.
- Do not diagnose diseases.
- Do not prescribe medication.
- Do not claim to cure or treat diseases.
- Do not present this as medical advice.

OUTPUT FORMAT
-------------
Use clear Markdown headings.

For example:

### Breakfast

**Food:** ...
**Portion:** ...
**Calories:** ...
**Protein:** ...

At the end provide:

### Daily Estimate

**Calories:** ...
**Protein:** ...

Finish with one short note explaining that the quantities
are approximate wellness estimates.
"""

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nourish, a careful and "
                                "practical nutrition assistant."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )

                answer = response.choices[0].message.content

                if not answer:
                    raise RuntimeError(
                        "The AI model returned an empty response."
                    )

                st.session_state.diet_response = answer
                st.session_state.diet_sources = docs

                status.update(
                    label="🥗 Your day is ready.",
                    state="complete",
                    expanded=False,
                )

            except Exception as error:

                status.update(
                    label="Nourish couldn't complete the plan.",
                    state="error",
                    expanded=True,
                )

                st.exception(error)


    # --------------------------------------------------------
    # DISPLAY GENERATED PLAN
    # --------------------------------------------------------

    if st.session_state.diet_response:

        st.divider()

        st.markdown(
            '<div class="section-label">Your plan</div>',
            unsafe_allow_html=True,
        )

        st.header("A simple day, built around you")

        st.markdown(
            st.session_state.diet_response
        )

        if st.session_state.diet_sources:

            with st.expander(
                "🔎 See the nutrition knowledge Nourish used"
            ):

                st.caption(
                    "Before generating the recommendation, Nourish "
                    "retrieved these relevant sections from the project's "
                    "nutrition knowledge base."
                )

                for index, document in enumerate(
                    st.session_state.diet_sources,
                    start=1,
                ):

                    st.markdown(
                        f"**Knowledge section {index}**"
                    )

                    st.write(
                        document.page_content
                    )


# ============================================================
# TAB 2 — ASK NOURISH
# ============================================================

with assistant_tab:

    st.markdown(
        '<div class="section-label">Nutrition assistant</div>',
        unsafe_allow_html=True,
    )

    st.header("Ask Nourish")

    st.write(
        "Have a nutrition question? Nourish first looks through "
        "its nutrition knowledge base, then uses the relevant "
        "information to formulate an answer."
    )

    question = st.text_area(
        "What would you like to know?",
        placeholder=(
            "Try: What are some good vegetarian sources of protein?"
        ),
        height=120,
    )

    ask_ai = st.button(
        "Ask Nourish",
        type="primary",
        use_container_width=True,
    )

    if ask_ai:

        if not question.strip():

            st.warning(
                "Ask a question first — even a simple one."
            )

        elif client is None:

            st.error(
                "The AI service isn't configured. "
                "Please make sure HF_TOKEN is available."
            )

        else:

            status = st.status(
                "🔎 Nourish is looking into that...",
                expanded=True,
            )

            try:

                # ------------------------------------------------
                # STEP 1 — RETRIEVAL
                # ------------------------------------------------

                status.write(
                    "📚 Searching the nutrition knowledge base..."
                )

                docs = search_nutrition(
                    question,
                    k=3,
                )

                if not docs:
                    raise RuntimeError(
                        "No relevant knowledge was retrieved."
                    )

                context = build_context(docs)

                status.write(
                    f"✓ Found {len(docs)} relevant knowledge sections"
                )

                # ------------------------------------------------
                # STEP 2 — LLM
                # ------------------------------------------------

                status.write(
                    "🧠 Nourish is thinking about your question..."
                )

                prompt = f"""
You are Nourish, an AI nutrition and wellness assistant.

Use the retrieved nutrition knowledge below to answer
the user's question clearly and accurately.

RETRIEVED NUTRITION KNOWLEDGE
-----------------------------
{context}

USER QUESTION
-------------
{question}

INSTRUCTIONS
------------
- Answer clearly and directly.
- Keep the explanation beginner-friendly.
- Prefer the retrieved knowledge when relevant.
- Do not invent medical facts.
- Do not diagnose diseases.
- Do not prescribe medicines.
- Do not claim to cure or treat diseases.
- If the question describes a serious or urgent medical concern,
  recommend consulting an appropriately qualified healthcare
  professional.
- Distinguish general nutrition information from medical advice.
"""

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nourish, a careful, "
                                "clear and beginner-friendly "
                                "nutrition assistant."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )

                answer = response.choices[0].message.content

                if not answer:
                    raise RuntimeError(
                        "The AI model returned an empty response."
                    )

                st.session_state.chat_response = answer
                st.session_state.chat_sources = docs

                status.update(
                    label="💬 Nourish has an answer.",
                    state="complete",
                    expanded=False,
                )

            except Exception as error:

                status.update(
                    label="Nourish couldn't answer that.",
                    state="error",
                    expanded=True,
                )

                st.exception(error)


    # --------------------------------------------------------
    # DISPLAY CHAT RESPONSE
    # --------------------------------------------------------

    if st.session_state.chat_response:

        st.divider()

        st.markdown(
            '<div class="section-label">Nourish says</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            st.session_state.chat_response
        )

        if st.session_state.chat_sources:

            with st.expander(
                "🔎 See what Nourish retrieved"
            ):

                st.caption(
                    "These are the relevant sections retrieved from "
                    "the nutrition knowledge base before the AI "
                    "generated the answer."
                )

                for index, document in enumerate(
                    st.session_state.chat_sources,
                    start=1,
                ):

                    st.markdown(
                        f"**Knowledge section {index}**"
                    )

                    st.write(
                        document.page_content
                    )


# ============================================================
# HOW NOURISH WORKS
# ============================================================

st.divider()

with st.expander("⚙️ How Nourish works"):

    st.markdown(
        """
### Behind the experience

**1. Your profile**

You provide basic information such as age, height, weight,
activity level, goal, diet preference and food restrictions.

**2. Python calculations**

Nourish calculates estimated BMI, BMR, TDEE and a daily
calorie target using deterministic Python functions.

**3. Knowledge retrieval**

Your nutrition question or meal-planning requirements are
used to search the project's nutrition knowledge base.

The knowledge base is built from the nutrition PDF using
embeddings and FAISS.

**4. AI generation**

The relevant retrieved information is combined with your
question or profile and sent to the language model.

**5. Final response**

Nourish turns that information into a readable answer or
one-day meal recommendation.

---

**Python handles the calculations.**

**RAG finds relevant knowledge.**

**The language model generates the response.**

**Streamlit brings everything together.**
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Nourish is an educational and general wellness project. "
    "Its calculations and AI-generated recommendations are estimates "
    "and are not a substitute for professional medical advice, "
    "diagnosis, or treatment."
)



#### GRAPHICAL INTTERFACE ####
# import streamlit as st
# import os
# from diet import bmi_calculator, bmr_calculator, calorie_target, tdee_calculator
# from dotenv import load_dotenv
# from openai import OpenAI
# from rag import load_rag

# ### LLM

# ### Accessing the API Key from the Token
# load_dotenv()
# HF_token = os.getenv("HF_TOKEN")

# client = OpenAI(
#     base_url = "https://router.huggingface.co/v1",
#     api_key = HF_token
#     )



# # st.page_setup(
# #     page_title = "Your AI Health Assistant!", 
# #     page_icon = "👍", 
# #     layout = "wide"
# #     )

# st.set_page_config(
#     page_title="Your AI Health Assistant!",
#     page_icon="👍",
#     layout="wide"
# )
# st.title("👍Your AI Health Assistant!")
# st.header("Didn't you become a little fat than yesterday? Check!")

# st.write("Personal Heatlh Assistance and Diet Recommendation System")

# st.sidebar.header("Your Information")

# gender = st.sidebar.selectbox("Select your Gender", ["male", "female"])
# age = st.sidebar.number_input("Enter your Age", 1, 100)
# weight = st.sidebar.number_input("Enter your Weight (in kg)", 1, 200)
# height = st.sidebar.number_input("Enter your Height (in cm)", 100, 250)
# activity = st.sidebar.selectbox("Select your Activity Level", 
#                                 ["Sedentary", 
#                                  "Lightly_Active", 
#                                  "Moderately_Active", 
#                                  "Very_Active", 
#                                  "Extra_Active"])
# aim = st.sidebar.selectbox("Select your Aim", ["weight maintain", "weight loss", "weight gain"])
# diet_type = st.sidebar.selectbox("Select your Diet Type:", ["Vegetarian", "Non-Vegetarian", "Vegan"])
# allergies = st.sidebar.selectbox("Slect your Allergies:", ["Allergic", "None"])

# bmi = bmi_calculator(weight, height)
# bmr = bmr_calculator(weight, height, age, gender)
# tdee = tdee_calculator(bmr, activity)
# calorie = calorie_target(tdee, aim)


# col1, col2, col3, col4 = st.columns(4)

# col1.metric("Your BMI", bmi)
# col2.metric("Your BMR",f"{bmr} kcal")
# col3.metric("Your TDEE", f"{tdee} kcal")
# col4.metric("Your Calorie Target", f"{calorie} kcal")


# tab1, tab2 = st.tabs(["Diet Recommendation", "Health Assistance"])

# if st.button("Get Recommendations"):
#     if client:
#         with st.spinner("Creating Diet..."):
#             try:
#                 db = load_rag()
#                 search_query = f"""
#                 Diet Type {diet_type}, 
#                 Healthy Food, 
#                 Protein, 
#                 Allergies {allergies}
#                 """
#                 # search_query = f"Recommend me a diet plan for {aim} with {calorie} calories."

#                 docs = db.similarity_search(search_query, 3)
#                 context = "\n\n".join([doc.page_content for doc in docs])
#                 prompt = f"""
# # **Diet Recommendation Prompt:**

# You are a helpful AI nutrition assistant.



# Use the following nutrition knowledge

# to create a simple one-day diet plan.



# NUTRITION KNOWLEDGE:



# {context}





# USER INFORMATION:



# Age: {age}



# Gender: {gender}



# Height: {height} cm



# Weight: {weight} kg



# Activity Level: {activity}



# aim: {aim}



# Diet Type: {diet_type}



# Food Allergy: {allergies}



# Estimated BMI: {bmi}



# Estimated BMR: {bmr} kcal/day



# Estimated TDEE: {tdee} kcal/day



# Estimated Daily Calorie Target:

# {calorie} kcal/day





# Create the following:



# 1\. Breakfast

# 2\. Morning Snack

# 3\. Lunch

# 4\. Evening Snack

# 5\. Dinner





# For every meal provide:



# \- Food

# \- Portion

# \- Approximate calories

# \- Approximate protein





# IMPORTANT RULES:



# \- Respect the user's diet type.

# \- Do not recommend foods containing

# &#x20; the stated allergy.

# \- Use the provided nutrition knowledge

# &#x20; when possible.

# \- Keep the plan simple and practical.

# \- Do not diagnose diseases.

# \- Do not prescribe medicines.

# \- Do not claim to cure diseases.

# \- This is general wellness information,

# &#x20; not medical advice.
# """
#                 response = client.chat.completions.create(
#                     model="openai/gpt-oss-120b",
#                     messages=[
#                         {"role": "user", "content": prompt}
#                     ]
#                 )
#                 answer = response.choices[0].message.content
#                 st.markdown(answer)
#             except:
#                 st.error("Error: Unable to generate recommendations. Please try again later.")

# if tab2:
#     question = st.text_area("Ask about Health", 
#                  placeholder = "Eg: Good source of vegetarian protein")
#     if st.button ("Ask AI"):
#         db = load_rag()
#         docs = db.similarity_search(question, 3)
#         context = "\n\n".join([doc.page_content for doc in docs])
#         prompt = f"""
# # **Chatbot Prompt:**
# You are an AI health and nutrition assistant.

# Use the following knowledge to answer the user's question.

# NUTRITION KNOWLEDGE: {context}

# USER QUESTION:

# {question}





# INSTRUCTIONS:



# \- Answer clearly.

# \- Keep the explanation beginner-friendly.

# \- Use the provided knowledge when possible.

# \- Do not invent medical facts.

# \- Do not diagnose diseases.

# \- Do not prescribe medicines.

# \- Do not claim to cure diseases.

# \- If the question concerns a serious

# &#x20; medical problem, recommend consulting

# &#x20; a qualified healthcare professional.



# This application provides general health

# and nutrition information for educational

# and wellness purposes.

# """             
#         response = client.chat.completions.create(
#                     model="openai/gpt-oss-120b",
#                         messages=[
#                                     {"role": "user", "content": prompt}
#                                 ]
#                             )
#         answer = response.choices[0].message.content
#         st.markdown(answer)