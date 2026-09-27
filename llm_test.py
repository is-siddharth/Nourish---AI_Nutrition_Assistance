"""
Simple diagnostic script for testing the LLM + RAG pipeline.

This is not part of the Streamlit application.

Run:

    python llm_test.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from rag import build_context, search_nutrition


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "openai/gpt-oss-120b"

TEST_QUESTION = (
    "What are some good sources of protein "
    "for a vegetarian diet?"
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# ============================================================
# CLIENT
# ============================================================

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN was not found. "
        "Check your .env configuration."
    )


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("=" * 60)
    print("NOURISH — LLM + RAG DIAGNOSTIC")
    print("=" * 60)

    print()
    print(f"Question: {TEST_QUESTION}")

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    print()
    print("Searching nutrition knowledge...")

    documents = search_nutrition(
        TEST_QUESTION,
        k=3,
    )

    if not documents:
        raise RuntimeError(
            "No relevant documents were retrieved."
        )

    context = build_context(
        documents
    )

    print(
        f"Retrieved {len(documents)} knowledge chunks."
    )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are Nourish, an AI nutrition and wellness assistant.

Use the retrieved nutrition knowledge below to answer
the user's question.

RETRIEVED KNOWLEDGE
-------------------
{context}

USER QUESTION
-------------
{TEST_QUESTION}

Give a clear, beginner-friendly answer.

Do not diagnose diseases.
Do not prescribe medicines.
Do not claim to cure diseases.
"""

    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    print()
    print("Sending context to the language model...")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Nourish, a careful "
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

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("NOURISH RESPONSE")
    print("=" * 60)
    print()

    print(answer)

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()


















# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# from rag import load_rag



# ### Accessing the API Key from the Token
# load_dotenv()
# HF_token = os.getenv("HF_TOKEN")

# client = OpenAI(
#     base_url = "https://router.huggingface.co/v1",
#     api_key = HF_token
#     )

# response = client.chat.completions.create(
#     model = "openai/gpt-oss-120b",
#     messages = [{
#         "role" : "user",
#         "content" : "What is good source of protein in Non-Vegetarian?"
#     }]
#     )

# answer = response.choices[0].message.content
# print(answer)






