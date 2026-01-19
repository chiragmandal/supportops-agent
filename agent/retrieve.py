from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

# If you don't have this installed yet:
# pip install -U langchain-text-splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --- Robust paths (always relative to repo root, not current working dir) ---
ROOT = Path(__file__).resolve().parents[1]   # repo root (agent/..)
KB_DIR = ROOT / "kb"
DB_DIR = ROOT / "chroma_db"


def _embedding() -> HuggingFaceEmbeddings:
    # Fast + good enough for KB retrieval
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_or_load_vectorstore() -> Chroma:
    """
    Build a Chroma vector store from markdown files in kb/ if not already persisted.
    Otherwise load the persisted store from chroma_db/.
    """
    if not KB_DIR.exists():
        raise FileNotFoundError(
            f"KB directory not found at: {KB_DIR}\n"
            f"Expected markdown files under {KB_DIR}/ (e.g., billing_policy.md)."
        )

    emb = _embedding()

    # Load existing persisted DB if present
    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        return Chroma(persist_directory=str(DB_DIR), embedding_function=emb)

    # Otherwise, build it from kb/*.md
    loaders: List[TextLoader] = []
    for p in KB_DIR.iterdir():
        if p.is_file() and p.suffix.lower() == ".md":
            loaders.append(TextLoader(str(p), encoding="utf-8"))

    if not loaders:
        raise FileNotFoundError(
            f"No .md files found in KB directory: {KB_DIR}\n"
            f"Add files like billing_policy.md, account_access.md, troubleshooting.md, security.md"
        )

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    splits = splitter.split_documents(docs)

    vs = Chroma.from_documents(
        documents=splits,
        embedding=emb,
        persist_directory=str(DB_DIR),
    )
    vs.persist()
    return vs


def retrieve(query: str, k: int = 5):
    """
    Retrieve top-k relevant KB chunks for a query.
    """
    vs = build_or_load_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)
