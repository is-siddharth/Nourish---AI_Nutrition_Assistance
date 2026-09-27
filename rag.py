"""
RAG utilities for Nourish.

Pipeline:

Nutrition PDF
      ↓
PDF Loader
      ↓
Text Chunks
      ↓
Embeddings
      ↓
FAISS Vector Store
      ↓
Semantic Retrieval
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PDF_FILE = BASE_DIR / "data" / "nutrition.pdf"
VECTOR_DB_DIR = BASE_DIR / "vector_db"


# ============================================================
# RAG CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

DEFAULT_TOP_K = 3


# ============================================================
# EMBEDDINGS
# ============================================================

def get_embeddings():
    """
    Create the embedding model used by the FAISS database.

    The same embedding model must be used when creating
    and loading the vector database.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# ============================================================
# DATABASE CREATION
# ============================================================

def create_rag() -> int:
    """
    Build the FAISS vector database from nutrition.pdf.

    Returns
    -------
    int
        Number of chunks created.
    """

    if not PDF_FILE.exists():
        raise FileNotFoundError(
            f"Nutrition PDF not found: {PDF_FILE}"
        )

    print("Loading nutrition knowledge...")

    documents = PyPDFLoader(
        str(PDF_FILE)
    ).load()

    if not documents:
        raise ValueError(
            "The nutrition PDF did not produce any documents."
        )

    print(
        f"Loaded {len(documents)} document pages."
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError(
            "No text chunks were created from the PDF."
        )

    print(
        f"Created {len(chunks)} text chunks."
    )

    print(
        f"Creating embeddings using: {EMBEDDING_MODEL}"
    )

    embeddings = get_embeddings()

    db = FAISS.from_documents(
        chunks,
        embeddings,
    )

    VECTOR_DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    db.save_local(
        str(VECTOR_DB_DIR)
    )

    print(
        f"FAISS database saved to: {VECTOR_DB_DIR}"
    )

    return len(chunks)


# ============================================================
# DATABASE LOADING
# ============================================================

def load_rag():
    """
    Load the existing FAISS nutrition database.
    """

    index_file = VECTOR_DB_DIR / "index.faiss"
    metadata_file = VECTOR_DB_DIR / "index.pkl"

    if not index_file.exists() or not metadata_file.exists():
        raise FileNotFoundError(
            "FAISS vector database not found. "
            "Run create_database.py first."
        )

    embeddings = get_embeddings()

    db = FAISS.load_local(
        str(VECTOR_DB_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return db


# ============================================================
# SEARCH HELPER
# ============================================================

def search_nutrition(
    query: str,
    k: int = DEFAULT_TOP_K,
):
    """
    Retrieve the most relevant nutrition documents
    for a user query.
    """

    if not query or not query.strip():
        raise ValueError(
            "Search query cannot be empty."
        )

    if k <= 0:
        raise ValueError(
            "Number of retrieved documents must be greater than zero."
        )

    db = load_rag()

    return db.similarity_search(
        query,
        k=k,
    )


# ============================================================
# CONTEXT BUILDER
# ============================================================

def build_context(
    documents,
) -> str:
    """
    Combine retrieved documents into a single context string
    for the language model.
    """

    if not documents:
        return ""

    return "\n\n".join(
        document.page_content
        for document in documents
    )














# import os
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings # Embedding: To convert Date --> Numbers
# from langchain_community.vectorstores import FAISS
# PDF_file = "data/nutrition.pdf"

# ## FAISS --> Vector Database
# ## What is a Vector_Database? 
# ## Database, where instead of data, binary value of the data is stored. 

# def create_rag():
#     if not os.path.exists(PDF_file):
#         raise FileNotFoundError("PDF file not found")
#     else:
#         document = PyPDFLoader(PDF_file).load()
#         splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap = 50)
#         chunks = splitter.split_documents(document)
#         embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
#         db = FAISS.from_documents(chunks, embeddings)
#         db.save_local("vector_db") 
#         return len(chunks)       

# def load_rag():
#     embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
#     db = FAISS.load_local("vector_db", embeddings, allow_dangerous_deserialization = True)
#     return db


