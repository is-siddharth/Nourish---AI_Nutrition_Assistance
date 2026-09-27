"""
Build the Nourish nutrition knowledge database.

Run:

    python create_database.py

This reads:

    data/nutrition.pdf

and creates:

    vector_db/
        index.faiss
        index.pkl
"""

from rag import create_rag


def main():
    print()
    print("=" * 55)
    print("NOURISH — NUTRITION KNOWLEDGE DATABASE")
    print("=" * 55)
    print()

    try:
        chunk_count = create_rag()

        print()
        print("-" * 55)
        print("Database creation complete.")
        print(f"Knowledge chunks indexed: {chunk_count}")
        print("-" * 55)
        print()

    except Exception as error:
        print()
        print("Database creation failed.")
        print(f"Reason: {error}")
        print()

        raise


if __name__ == "__main__":
    main()











# from rag import create_rag

# print("Creating Database...")
# create_rag()
# print("Database Created!")