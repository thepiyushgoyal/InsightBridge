from __future__ import annotations

import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.loaders import load_knowledge_base


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_BASE_DIR = ROOT_DIR / "data" / "knowledge_base"
DEFAULT_INDEX_DIR = ROOT_DIR / "data" / "faiss_index"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def ensure_openai_api_key() -> None:
    """Fail early with a friendly message when OpenAI credentials are missing."""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Add it to your environment or a local .env file."
        )


def split_documents(
    documents: list[Document],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Split source documents into citation-friendly chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)

    counters: dict[str, int] = {}
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        counters[source] = counters.get(source, 0) + 1
        chunk.metadata["chunk_id"] = counters[source]

    return chunks


def get_embeddings() -> OpenAIEmbeddings:
    """Create the embedding client used by FAISS."""
    ensure_openai_api_key()
    return OpenAIEmbeddings(model=DEFAULT_EMBEDDING_MODEL)


def build_vector_index(
    knowledge_base_dir: Path = DEFAULT_KNOWLEDGE_BASE_DIR,
    index_dir: Path = DEFAULT_INDEX_DIR,
) -> int:
    """Load, chunk, embed, and persist the local FAISS index."""
    documents = load_knowledge_base(knowledge_base_dir)
    chunks = split_documents(documents)
    if not chunks:
        raise ValueError("Documents were loaded, but no chunks were created.")

    vector_store = FAISS.from_documents(chunks, get_embeddings())
    index_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_dir))
    return len(chunks)


def load_vector_index(index_dir: Path = DEFAULT_INDEX_DIR) -> FAISS:
    """Load a previously built FAISS index from disk."""
    ensure_openai_api_key()
    if not index_dir.exists() or not (index_dir / "index.faiss").exists():
        raise FileNotFoundError("FAISS index has not been built yet.")

    return FAISS.load_local(
        str(index_dir),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def index_exists(index_dir: Path = DEFAULT_INDEX_DIR) -> bool:
    """Return True when the persisted FAISS files are present."""
    return index_dir.exists() and (index_dir / "index.faiss").exists()
