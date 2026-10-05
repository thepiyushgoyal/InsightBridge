from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.ingestion import split_documents
from src.loaders import load_knowledge_base


def main() -> None:
    """Validate local document loading and chunking without calling OpenAI."""
    knowledge_base_dir = ROOT_DIR / "data" / "knowledge_base"
    documents = load_knowledge_base(knowledge_base_dir)
    chunks = split_documents(documents)

    assert documents, "Expected at least one loaded document."
    assert chunks, "Expected at least one generated chunk."
    assert all("source" in chunk.metadata for chunk in chunks), "Every chunk needs source metadata."

    print(f"Loaded {len(documents)} documents and created {len(chunks)} chunks.")


if __name__ == "__main__":
    main()
