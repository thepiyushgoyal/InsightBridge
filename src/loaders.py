from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader


SUPPORTED_EXTENSIONS = {".md", ".txt", ".csv", ".sql", ".pdf"}


def load_knowledge_base(knowledge_base_dir: Path) -> list[Document]:
    """Load supported documents from the local knowledge base directory."""
    if not knowledge_base_dir.exists():
        raise FileNotFoundError(f"Knowledge base folder not found: {knowledge_base_dir}")

    documents: list[Document] = []
    for file_path in sorted(knowledge_base_dir.iterdir()):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        loaded_docs = _load_file(file_path)
        for doc in loaded_docs:
            doc.metadata["source"] = file_path.name
            doc.metadata["file_path"] = str(file_path)
        documents.extend(loaded_docs)

    if not documents:
        raise ValueError(
            f"No supported documents found in {knowledge_base_dir}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    return documents


def _load_file(file_path: Path) -> list[Document]:
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        loader = CSVLoader(file_path=str(file_path), encoding="utf-8")
    elif suffix == ".pdf":
        loader = PyPDFLoader(str(file_path))
    else:
        loader = TextLoader(str(file_path), encoding="utf-8")

    return loader.load()
